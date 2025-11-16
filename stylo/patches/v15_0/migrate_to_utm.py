import stylo


def execute():
	"""
	Rename the Marketing Campaign table to UTM Campaign table
	"""
	if stylo.db.exists("DocType", "UTM Campaign"):
		return

	if not stylo.db.exists("DocType", "Marketing Campaign"):
		return

	stylo.rename_doc("DocType", "Marketing Campaign", "UTM Campaign", force=True)
	stylo.reload_doctype("UTM Campaign", force=True)
