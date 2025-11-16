# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import getpass

import stylo
from stylo.geo.doctype.country.country import import_country_and_currency
from stylo.utils import cint
from stylo.utils.password import update_password


def before_install():
	stylo.reload_doc("core", "doctype", "doctype_state")
	stylo.reload_doc("core", "doctype", "docfield")
	stylo.reload_doc("core", "doctype", "docperm")
	stylo.reload_doc("core", "doctype", "doctype_action")
	stylo.reload_doc("core", "doctype", "doctype_link")
	stylo.reload_doc("desk", "doctype", "form_tour_step")
	stylo.reload_doc("desk", "doctype", "form_tour")
	stylo.reload_doc("core", "doctype", "doctype")
	stylo.clear_cache()


def after_install():
	create_user_type()
	install_basic_docs()

	from stylo.core.doctype.file.utils import make_home_folder
	from stylo.core.doctype.language.language import sync_languages

	make_home_folder()
	import_country_and_currency()
	sync_languages()

	# save default print setting
	print_settings = stylo.get_doc("Print Settings")
	print_settings.save()

	# all roles to admin
	stylo.get_doc("User", "Administrator").add_roles(*stylo.get_all("Role", pluck="name"))

	# update admin password
	update_password("Administrator", get_admin_password())

	if not stylo.conf.skip_setup_wizard:
		# only set home_page if the value doesn't exist in the db
		if not stylo.db.get_default("desktop:home_page"):
			stylo.db.set_default("desktop:home_page", "setup-wizard")

	# clear test log
	from stylo.tests.utils.generators import _clear_test_log

	_clear_test_log()

	add_standard_navbar_items()

	stylo.db.commit()


def create_user_type():
	for user_type in ["System User", "Website User"]:
		if not stylo.db.exists("User Type", user_type):
			stylo.get_doc({"doctype": "User Type", "name": user_type, "is_standard": 1}).insert(
				ignore_permissions=True
			)


def install_basic_docs():
	# core users / roles
	install_docs = [
		{
			"doctype": "User",
			"name": "Administrator",
			"first_name": "Administrator",
			"email": "admin@example.com",
			"enabled": 1,
			"is_admin": 1,
			"roles": [{"role": "Administrator"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{
			"doctype": "User",
			"name": "Guest",
			"first_name": "Guest",
			"email": "guest@example.com",
			"enabled": 1,
			"is_guest": 1,
			"roles": [{"role": "Guest"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Pending",
			"icon": "question-sign",
			"style": "",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Approved",
			"icon": "ok-sign",
			"style": "Success",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Rejected",
			"icon": "remove",
			"style": "Danger",
		},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Approve"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Reject"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Review"},
	]

	for d in install_docs:
		try:
			stylo.get_doc(d).insert(ignore_if_duplicate=True)
		except stylo.NameError:
			pass


def get_admin_password():
	return stylo.conf.get("admin_password") or getpass.getpass("Set Administrator password: ")


def before_tests():
	if len(stylo.get_installed_apps()) > 1:
		# don't run before tests if any other app is installed
		return

	stylo.db.truncate("Custom Field")
	stylo.db.truncate("Event")

	stylo.clear_cache()

	# complete setup if missing
	if not stylo.is_setup_complete():
		complete_setup_wizard()

	stylo.db.set_single_value("Website Settings", "disable_signup", 0)
	stylo.db.commit()
	stylo.clear_cache()


def complete_setup_wizard():
	from stylo.desk.page.setup_wizard.setup_wizard import setup_complete

	setup_complete(
		{
			"language": "English",
			"email": "test@erpnext.com",
			"full_name": "Test User",
			"password": "test",
			"country": "United States",
			"timezone": "America/New_York",
			"currency": "USD",
			"enable_telemtry": 1,
		}
	)


def add_standard_navbar_items():
	navbar_settings = stylo.get_single("Navbar Settings")

	# don't add settings/help options if they're already present
	if navbar_settings.settings_dropdown and navbar_settings.help_dropdown:
		return

	navbar_settings.settings_dropdown = []
	navbar_settings.help_dropdown = []

	for item in stylo.get_hooks("standard_navbar_items"):
		navbar_settings.append("settings_dropdown", item)

	for item in stylo.get_hooks("standard_help_items"):
		navbar_settings.append("help_dropdown", item)

	navbar_settings.save()
