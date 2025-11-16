# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	stylo.reload_doc("core", "doctype", "system_settings", force=1)
	stylo.db.set_single_value("System Settings", "password_reset_limit", 3)
