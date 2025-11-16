# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	stylo.reload_doc("core", "doctype", "DocField")

	if stylo.db.has_column("DocField", "show_days"):
		stylo.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_days = 1 WHERE show_days = 0
		"""
		)
		stylo.db.sql_ddl("alter table tabDocField drop column show_days")

	if stylo.db.has_column("DocField", "show_seconds"):
		stylo.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_seconds = 1 WHERE show_seconds = 0
		"""
		)
		stylo.db.sql_ddl("alter table tabDocField drop column show_seconds")

	stylo.clear_cache(doctype="DocField")
