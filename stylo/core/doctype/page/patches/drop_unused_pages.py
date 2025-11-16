import stylo


def execute():
	for name in ("desktop", "space"):
		stylo.delete_doc("Page", name)
