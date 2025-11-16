import stylo


def execute():
	singles = stylo.qb.Table("tabSingles")
	stylo.qb.from_(singles).delete().where(
		(singles.doctype == "System Settings") & (singles.field == "is_first_startup")
	).run()
