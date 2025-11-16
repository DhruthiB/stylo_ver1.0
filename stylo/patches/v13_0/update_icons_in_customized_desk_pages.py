import stylo


def execute():
	if not stylo.db.exists("Desk Page"):
		return

	pages = stylo.get_all(
		"Desk Page", filters={"is_standard": False}, fields=["name", "extends", "for_user"]
	)
	default_icon = {}
	for page in pages:
		if page.extends and page.for_user:
			if not default_icon.get(page.extends):
				default_icon[page.extends] = stylo.db.get_value("Desk Page", page.extends, "icon")

			icon = default_icon.get(page.extends)
			stylo.db.set_value("Desk Page", page.name, "icon", icon)
