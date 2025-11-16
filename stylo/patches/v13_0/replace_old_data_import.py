# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	if not stylo.db.table_exists("Data Import"):
		return

	meta = stylo.get_meta("Data Import")
	# if Data Import is the new one, return early
	if meta.fields[1].fieldname == "import_type":
		return

	stylo.db.sql("DROP TABLE IF EXISTS `tabData Import Legacy`")
	stylo.rename_doc("DocType", "Data Import", "Data Import Legacy")
	stylo.db.commit()
	stylo.db.sql("DROP TABLE IF EXISTS `tabData Import`")
	stylo.rename_doc("DocType", "Data Import Beta", "Data Import")
