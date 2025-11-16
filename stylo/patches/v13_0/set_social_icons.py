import stylo


def execute():
	providers = stylo.get_all("Social Login Key")

	for provider in providers:
		doc = stylo.get_doc("Social Login Key", provider)
		doc.set_icon()
		doc.save()
