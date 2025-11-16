import stylo


def execute():
	column = "apply_user_permissions"
	to_remove = ["DocPerm", "Custom DocPerm"]

	for doctype in to_remove:
		if stylo.db.table_exists(doctype):
			if column in stylo.db.get_table_columns(doctype):
				stylo.db.sql(f"alter table `tab{doctype}` drop column {column}")

	stylo.reload_doc("core", "doctype", "docperm", force=True)
	stylo.reload_doc("core", "doctype", "custom_docperm", force=True)
