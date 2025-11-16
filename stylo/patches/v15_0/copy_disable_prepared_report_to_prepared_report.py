import stylo


def execute():
	table = stylo.qb.DocType("Report")
	stylo.qb.update(table).set(table.prepared_report, 0).where(table.disable_prepared_report == 1)
