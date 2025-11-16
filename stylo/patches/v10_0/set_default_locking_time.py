# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	stylo.reload_doc("core", "doctype", "system_settings")
	stylo.db.set_single_value("System Settings", "allow_login_after_fail", 60)
