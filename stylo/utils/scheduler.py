# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
"""
Events:
	always
	daily
	monthly
	weekly
"""

# imports - standard imports
import os
import random
import time

from croniter import CroniterBadCronError

# imports - module imports
import stylo
from stylo.utils import cint, get_datetime, get_sites, now_datetime
from stylo.utils.background_jobs import get_jobs, set_niceness

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def cprint(*args, **kwargs):
	"""Prints only if called from STDOUT"""
	try:
		os.get_terminal_size()
		print(*args, **kwargs)
	except Exception:
		pass


def start_scheduler():
	"""Run enqueue_events_for_all_sites based on scheduler tick.
	Specify scheduler_interval in seconds in common_site_config.json"""

	tick = get_scheduler_tick()
	set_niceness()

	while True:
		time.sleep(tick)
		enqueue_events_for_all_sites()


def enqueue_events_for_all_sites():
	"""Loop through sites and enqueue events that are not already queued"""

	if os.path.exists(os.path.join(".", ".restarting")):
		# Don't add task to queue if webserver is in restart mode
		return

	with stylo.init_site():
		sites = get_sites()

	# Sites are sorted in alphabetical order, shuffle to randomize priorities
	random.shuffle(sites)

	for site in sites:
		try:
			enqueue_events_for_site(site=site)
		except Exception as e:
			print(e.__class__, f"Failed to enqueue events for site: {site}")


def enqueue_events_for_site(site):
	def log_and_raise():
		error_message = f"Exception in Enqueue Events for Site {site}\n{stylo.get_traceback()}"
		stylo.logger("scheduler").error(error_message)

	try:
		stylo.init(site=site)
		stylo.connect()
		if is_scheduler_inactive():
			return

		enqueue_events(site=site)

		stylo.logger("scheduler").debug(f"Queued events for site {site}")
	except stylo.db.OperationalError as e:
		if stylo.db.is_access_denied(e):
			stylo.logger("scheduler").debug(f"Access denied for site {site}")
		else:
			log_and_raise()
	except Exception:
		log_and_raise()

	finally:
		stylo.destroy()


def enqueue_events(site):
	if schedule_jobs_based_on_activity():
		stylo.flags.enqueued_jobs = []
		queued_jobs = get_jobs(site=site, key="job_type").get(site) or []
		for job_type in stylo.get_all("Scheduled Job Type", ("name", "method"), dict(stopped=0)):
			if job_type.method not in queued_jobs:
				# don't add it to queue if still pending
				try:
					stylo.get_doc("Scheduled Job Type", job_type.name).enqueue()
				except CroniterBadCronError:
					stylo.logger("scheduler").error(
						f"Invalid Job on {stylo.local.site} - {job_type.name}", exc_info=True
					)


def is_scheduler_inactive(verbose=True) -> bool:
	if stylo.local.conf.maintenance_mode:
		if verbose:
			cprint(f"{stylo.local.site}: Maintenance mode is ON")
		return True

	if stylo.local.conf.pause_scheduler:
		if verbose:
			cprint(f"{stylo.local.site}: stylo.conf.pause_scheduler is SET")
		return True

	if is_scheduler_disabled(verbose=verbose):
		return True

	return False


def is_scheduler_disabled(verbose=True) -> bool:
	if stylo.conf.disable_scheduler:
		if verbose:
			cprint(f"{stylo.local.site}: stylo.conf.disable_scheduler is SET")
		return True

	scheduler_disabled = not stylo.utils.cint(
		stylo.db.get_single_value("System Settings", "enable_scheduler")
	)
	if scheduler_disabled:
		if verbose:
			cprint(f"{stylo.local.site}: SystemSettings.enable_scheduler is UNSET")
	return scheduler_disabled


def toggle_scheduler(enable):
	stylo.db.set_single_value("System Settings", "enable_scheduler", int(enable))


def enable_scheduler():
	toggle_scheduler(True)


def disable_scheduler():
	toggle_scheduler(False)


def schedule_jobs_based_on_activity(check_time=None):
	"""Returns True for active sites defined by Activity Log
	Returns True for inactive sites once in 24 hours"""
	if is_dormant(check_time=check_time):
		# ensure last job is one day old
		last_job_timestamp = _get_last_modified_timestamp("Scheduled Job Log")
		if not last_job_timestamp:
			return True
		else:
			if ((check_time or now_datetime()) - last_job_timestamp).total_seconds() >= 86400:
				# one day is passed since jobs are run, so lets do this
				return True
			else:
				# schedulers run in the last 24 hours, do nothing
				return False
	else:
		# site active, lets run the jobs
		return True


def is_dormant(check_time=None):
	# Assume never dormant if developer_mode is enabled
	if stylo.conf.developer_mode:
		return False
	last_activity_log_timestamp = _get_last_modified_timestamp("Activity Log")
	since = (stylo.get_system_settings("dormant_days") or 4) * 86400
	if not last_activity_log_timestamp:
		return True
	if ((check_time or now_datetime()) - last_activity_log_timestamp).total_seconds() >= since:
		return True
	return False


def _get_last_modified_timestamp(doctype):
	timestamp = stylo.db.get_value(doctype, filters={}, fieldname="modified", order_by="modified desc")
	if timestamp:
		return get_datetime(timestamp)


@stylo.whitelist()
def activate_scheduler():
	from stylo.installer import update_site_config

	stylo.only_for("Administrator")

	if stylo.local.conf.maintenance_mode:
		stylo.throw(stylo._("Scheduler can not be re-enabled when maintenance mode is active."))

	if is_scheduler_disabled():
		enable_scheduler()
	if stylo.conf.pause_scheduler:
		update_site_config("pause_scheduler", 0)


@stylo.whitelist()
def get_scheduler_status():
	if is_scheduler_inactive():
		return {"status": "inactive"}
	return {"status": "active"}


def get_scheduler_tick() -> int:
	return cint(stylo.get_conf().scheduler_tick_interval) or 60
