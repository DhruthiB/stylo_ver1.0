# Copyright (c) 2019, Stylo Technologies and contributors
# License: MIT. See LICENSE

from types import FunctionType, MethodType, ModuleType

import stylo
from stylo import _
from stylo.model.document import Document
from stylo.utils.safe_exec import NamespaceDict, get_safe_globals, safe_exec


class ServerScript(Document):
	def validate(self):
		stylo.only_for("Script Manager", True)
		self.sync_scheduled_jobs()
		self.clear_scheduled_events()
		self.check_if_compilable_in_restricted_context()

	def on_update(self):
		self.sync_scheduler_events()

	def clear_cache(self):
		stylo.cache().delete_value("server_script_map")
		return super().clear_cache()

	def on_trash(self):
		if self.script_type == "Scheduler Event":
			for job in self.scheduled_jobs:
				stylo.delete_doc("Scheduled Job Type", job.name)

	def get_code_fields(self):
		return {"script": "py"}

	@property
	def scheduled_jobs(self) -> list[dict[str, str]]:
		return stylo.get_all(
			"Scheduled Job Type",
			filters={"server_script": self.name},
			fields=["name", "stopped"],
		)

	def sync_scheduled_jobs(self):
		"""Sync Scheduled Job Type statuses if Server Script's disabled status is changed"""
		if self.script_type != "Scheduler Event" or not self.has_value_changed("disabled"):
			return

		for scheduled_job in self.scheduled_jobs:
			if bool(scheduled_job.stopped) != bool(self.disabled):
				job = stylo.get_doc("Scheduled Job Type", scheduled_job.name)
				job.stopped = self.disabled
				job.save()

	def sync_scheduler_events(self):
		"""Create or update Scheduled Job Type documents for Scheduler Event Server Scripts"""
		if not self.disabled and self.event_frequency and self.script_type == "Scheduler Event":
			cron_format = self.cron_format if self.event_frequency == "Cron" else None
			setup_scheduler_events(
				script_name=self.name, frequency=self.event_frequency, cron_format=cron_format
			)

	def clear_scheduled_events(self):
		"""Deletes existing scheduled jobs by Server Script if self.event_frequency or self.cron_format has changed"""
		if (
			self.script_type == "Scheduler Event"
			and (self.has_value_changed("event_frequency") or self.has_value_changed("cron_format"))
		) or (self.has_value_changed("script_type") and self.script_type != "Scheduler Event"):
			for scheduled_job in self.scheduled_jobs:
				stylo.delete_doc("Scheduled Job Type", scheduled_job.name, delete_permanently=1)

	def check_if_compilable_in_restricted_context(self):
		"""Check compilation errors and send them back as warnings."""
		from RestrictedPython import compile_restricted

		try:
			compile_restricted(self.script)
		except Exception as e:
			stylo.msgprint(str(e), title=_("Compilation warning"))

	def execute_method(self) -> dict:
		"""Specific to API endpoint Server Scripts

		Raises:
		        stylo.DoesNotExistError: If self.script_type is not API
		        stylo.PermissionError: If self.allow_guest is unset for API accessed by Guest user

		Returns:
		        dict: Evaluates self.script with stylo.utils.safe_exec.safe_exec and returns the flags set in it's safe globals
		"""
		# wrong report type!
		if self.script_type != "API":
			raise stylo.DoesNotExistError

		# validate if guest is allowed
		if stylo.session.user == "Guest" and not self.allow_guest:
			raise stylo.PermissionError

		# output can be stored in flags
		_globals, _locals = safe_exec(self.script)
		return _globals.stylo.flags

	def execute_doc(self, doc: Document):
		"""Specific to Document Event triggered Server Scripts

		Args:
		        doc (Document): Executes script with for a certain document's events
		"""
		safe_exec(self.script, _locals={"doc": doc}, restrict_commit_rollback=True)

	def execute_scheduled_method(self):
		"""Specific to Scheduled Jobs via Server Scripts

		Raises:
		        stylo.DoesNotExistError: If script type is not a scheduler event
		"""
		if self.script_type != "Scheduler Event":
			raise stylo.DoesNotExistError

		safe_exec(self.script)

	def get_permission_query_conditions(self, user: str) -> list[str]:
		"""Specific to Permission Query Server Scripts

		Args:
		        user (str): Takes user email to execute script and return list of conditions

		Returns:
		        list: Returns list of conditions defined by rules in self.script
		"""
		locals = {"user": user, "conditions": ""}
		safe_exec(self.script, None, locals)
		if locals["conditions"]:
			return locals["conditions"]

	@stylo.whitelist()
	def get_autocompletion_items(self):
		"""Generates a list of a autocompletion strings from the context dict
		that is used while executing a Server Script.

		Returns:
		        list: Returns list of autocompletion items.
		        For e.g., ["stylo.utils.cint", "stylo.get_all", ...]
		"""

		def get_keys(obj):
			out = []
			for key in obj:
				if key.startswith("_"):
					continue
				value = obj[key]
				if isinstance(value, NamespaceDict | dict) and value:
					if key == "form_dict":
						out.append(["form_dict", 7])
						continue
					for subkey, score in get_keys(value):
						fullkey = f"{key}.{subkey}"
						out.append([fullkey, score])
				else:
					if isinstance(value, type) and issubclass(value, Exception):
						score = 0
					elif isinstance(value, ModuleType):
						score = 10
					elif isinstance(value, FunctionType | MethodType):
						score = 9
					elif isinstance(value, type):
						score = 8
					elif isinstance(value, dict):
						score = 7
					else:
						score = 6
					out.append([key, score])
			return out

		items = stylo.cache().get_value("server_script_autocompletion_items")
		if not items:
			items = get_keys(get_safe_globals())
			items = [{"value": d[0], "score": d[1]} for d in items]
			stylo.cache().set_value("server_script_autocompletion_items", items)
		return items


def setup_scheduler_events(script_name: str, frequency: str, cron_format: str | None = None):
	"""Creates or Updates Scheduled Job Type documents based on the specified script name and frequency

	Args:
	        script_name (str): Name of the Server Script document
	        frequency (str): Event label compatible with the Stylo scheduler
	"""
	method = stylo.scrub(f"{script_name}-{frequency}")
	scheduled_script = stylo.db.get_value("Scheduled Job Type", {"method": method})

	if not scheduled_script:
		stylo.get_doc(
			{
				"doctype": "Scheduled Job Type",
				"method": method,
				"frequency": frequency,
				"server_script": script_name,
				"cron_format": cron_format,
			}
		).insert()

		stylo.msgprint(_("Enabled scheduled execution for script {0}").format(script_name))

	else:
		doc = stylo.get_doc("Scheduled Job Type", scheduled_script)

		if doc.frequency == frequency:
			return

		doc.frequency = frequency
		doc.cron_format = cron_format
		doc.save()

		stylo.msgprint(_("Scheduled execution for script {0} has updated").format(script_name))
