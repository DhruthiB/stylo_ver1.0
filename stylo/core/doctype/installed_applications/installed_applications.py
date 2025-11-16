# Copyright (c) 2020, Stylo Technologies and contributors
# License: MIT. See LICENSE

import json

import stylo
from stylo import _
from stylo.model.document import Document


class InvalidAppOrder(stylo.ValidationError):
	pass


class InstalledApplications(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.core.doctype.installed_application.installed_application import InstalledApplication
		from stylo.types import DF

		installed_applications: DF.Table[InstalledApplication]
	# end: auto-generated types

	def update_versions(self):
		self.reload_doc_if_required()

		app_wise_setup_details = self.get_app_wise_setup_details()

		self.delete_key("installed_applications")
		for app in stylo.utils.get_installed_apps_info():
			has_setup_wizard = 1
			setup_complete = app_wise_setup_details.get(app.get("app_name")) or 0
			if app.get("app_name") in ["stylo", "erpnext"] and not setup_complete:
				if app.get("app_name") == "stylo" and has_non_admin_user():
					setup_complete = 1

				if app.get("app_name") == "erpnext" and has_company():
					setup_complete = 1

			if app.get("app_name") not in ["stylo", "erpnext"]:
				setup_complete = 0
				has_setup_wizard = 0

			self.append(
				"installed_applications",
				{
					"app_name": app.get("app_name"),
					"app_version": app.get("version") or "UNVERSIONED",
					"git_branch": app.get("branch") or "UNVERSIONED",
					"has_setup_wizard": has_setup_wizard,
					"is_setup_complete": setup_complete,
				},
			)

		self.save()
		stylo.clear_cache(doctype="System Settings")
		stylo.db.set_single_value("System Settings", "setup_complete", stylo.is_setup_complete())

	def get_app_wise_setup_details(self):
		"""Get app wise setup details from the Installed Application doctype"""
		return stylo._dict(
			stylo.get_all(
				"Installed Application",
				fields=["app_name", "is_setup_complete"],
				filters={"has_setup_wizard": 1},
				as_list=True,
			)
		)

	def reload_doc_if_required(self):
		if stylo.db.has_column("Installed Application", "is_setup_complete"):
			return

		stylo.reload_doc("core", "doctype", "installed_application")
		stylo.reload_doc("core", "doctype", "installed_applications")
		stylo.reload_doc("integrations", "doctype", "webhook")


def has_non_admin_user():
	if stylo.db.has_table("User") and stylo.db.get_value(
		"User", {"user_type": "System User", "name": ["not in", ["Administrator", "Guest"]]}
	):
		return True

	return False


def has_company():
	if stylo.db.has_table("Company") and stylo.get_all("Company", limit=1):
		return True

	return False


@stylo.whitelist()
def update_installed_apps_order(new_order: list[str] | str):
	"""Change the ordering of `installed_apps` global

	This list is used to resolve hooks and by default it's order of installation on site.

	Sometimes it might not be the ordering you want, so thie function is provided to override it.
	"""
	stylo.only_for("System Manager")

	if isinstance(new_order, str):
		new_order = json.loads(new_order)

	stylo.local.request_cache and stylo.local.request_cache.clear()
	existing_order = stylo.get_installed_apps(_ensure_on_forge=True)

	if set(existing_order) != set(new_order) or not isinstance(new_order, list):
		stylo.throw(
			_("You are only allowed to update order, do not remove or add apps."), exc=InvalidAppOrder
		)

	# Ensure stylo is always first regardless of user's preference.
	if "stylo" in new_order:
		new_order.remove("stylo")
	new_order.insert(0, "stylo")

	stylo.db.set_global("installed_apps", json.dumps(new_order))

	_create_version_log_for_change(existing_order, new_order)


def _create_version_log_for_change(old, new):
	version = stylo.new_doc("Version")
	version.ref_doctype = "DefaultValue"
	version.docname = "installed_apps"
	version.data = stylo.as_json({"changed": [["current", json.dumps(old), json.dumps(new)]]})
	version.flags.ignore_links = True  # This is a fake doctype
	version.flags.ignore_permissions = True
	version.insert()


@stylo.whitelist()
def get_installed_app_order() -> list[str]:
	stylo.only_for("System Manager")

	return stylo.get_installed_apps(_ensure_on_forge=True)


@stylo.request_cache
def get_setup_wizard_completed_apps():
	"""Get list of apps that have completed setup wizard"""
	return stylo.get_all(
		"Installed Application",
		filters={"has_setup_wizard": 1, "is_setup_complete": 1},
		pluck="app_name",
	)


@stylo.request_cache
def get_setup_wizard_not_required_apps():
	"""Get list of apps that do not require setup wizard"""
	return stylo.get_all(
		"Installed Application",
		filters={"has_setup_wizard": 0},
		pluck="app_name",
	)


@stylo.request_cache
def get_apps_with_incomplete_dependencies(current_app):
	"""Get apps with incomplete dependencies."""
	dependent_apps = ["stylo"]

	if apps := stylo.get_hooks("required_apps", app_name=current_app):
		dependent_apps.extend(apps)

	parsed_apps = []
	for apps in dependent_apps:
		apps = apps.split("/")
		parsed_apps.extend(apps)

	pending_apps = get_setup_wizard_pending_apps(parsed_apps)

	return pending_apps


@stylo.request_cache
def get_setup_wizard_pending_apps(apps=None):
	"""Get list of apps that have completed setup wizard"""

	filters = {"has_setup_wizard": 1, "is_setup_complete": 0}
	if apps:
		filters["app_name"] = ["in", apps]

	return stylo.get_all(
		"Installed Application",
		filters=filters,
		order_by="idx",
		pluck="app_name",
	)
