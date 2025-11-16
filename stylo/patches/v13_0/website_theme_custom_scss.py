import stylo


def execute():
	stylo.reload_doc("website", "doctype", "website_theme_ignore_app")
	stylo.reload_doc("website", "doctype", "color")
	stylo.reload_doc("website", "doctype", "website_theme")
	stylo.reload_doc("website", "doctype", "website_settings")

	for theme in stylo.get_all("Website Theme"):
		doc = stylo.get_doc("Website Theme", theme.name)
		if not doc.get("custom_scss") and doc.theme_scss:
			# move old theme to new theme
			doc.custom_scss = doc.theme_scss

			if doc.background_color:
				setup_color_record(doc.background_color)

			doc.save()


def setup_color_record(color):
	stylo.get_doc(
		{
			"doctype": "Color",
			"__newname": color,
			"color": color,
		}
	).save()
