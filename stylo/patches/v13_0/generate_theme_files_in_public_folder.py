# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	stylo.reload_doc("website", "doctype", "website_theme_ignore_app")
	themes = stylo.get_all("Website Theme", filters={"theme_url": ("not like", "/files/website_theme/%")})
	for theme in themes:
		doc = stylo.get_doc("Website Theme", theme.name)
		try:
			doc.save()
		except Exception:
			print("Ignoring....")
			print(stylo.get_traceback())
