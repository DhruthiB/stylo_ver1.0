import stylo


def execute():
	stylo.reload_doctype("Letter Head")

	# source of all existing letter heads must be HTML
	stylo.db.sql("update `tabLetter Head` set source = 'HTML'")
