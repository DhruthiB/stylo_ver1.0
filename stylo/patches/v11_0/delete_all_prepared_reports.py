import stylo


def execute():
	if stylo.db.table_exists("Prepared Report"):
		stylo.reload_doc("core", "doctype", "prepared_report")
		prepared_reports = stylo.get_all("Prepared Report")
		for report in prepared_reports:
			stylo.delete_doc("Prepared Report", report.name)
