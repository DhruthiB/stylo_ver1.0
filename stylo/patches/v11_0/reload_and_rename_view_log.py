import stylo


def execute():
	if stylo.db.table_exists("View log"):
		# for mac users direct renaming would not work since mysql for mac saves table name in lower case
		# so while renaming `tabView log` to `tabView Log` we get "Table 'tabView Log' already exists" error
		# more info https://stackoverflow.com/a/44753093/5955589 ,
		# https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_lower_case_table_names

		# here we are creating a temp table to store view log data
		stylo.db.sql("CREATE TABLE `ViewLogTemp` AS SELECT * FROM `tabView log`")

		# deleting old View log table
		stylo.db.sql("DROP table `tabView log`")
		stylo.delete_doc("DocType", "View log")

		# reloading view log doctype to create `tabView Log` table
		stylo.reload_doc("core", "doctype", "view_log")

		# Move the data to newly created `tabView Log` table
		stylo.db.sql("INSERT INTO `tabView Log` SELECT * FROM `ViewLogTemp`")
		stylo.db.commit()

		# Delete temporary table
		stylo.db.sql("DROP table `ViewLogTemp`")
	else:
		stylo.reload_doc("core", "doctype", "view_log")
