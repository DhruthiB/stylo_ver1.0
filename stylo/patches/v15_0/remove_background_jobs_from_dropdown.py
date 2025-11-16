import stylo


def execute():
	item = stylo.db.exists("Navbar Item", {"item_label": "Background Jobs"})
	if not item:
		return

	stylo.delete_doc("Navbar Item", item)
