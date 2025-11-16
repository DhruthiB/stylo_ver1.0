import stylo


def execute():
	categories = stylo.get_list("Blog Category")
	for category in categories:
		doc = stylo.get_doc("Blog Category", category["name"])
		doc.set_route()
		doc.save()
