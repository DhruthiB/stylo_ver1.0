# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	"""Set default module for standard Web Template, if none."""
	stylo.reload_doc("website", "doctype", "Web Template Field")
	stylo.reload_doc("website", "doctype", "web_template")

	standard_templates = stylo.get_list("Web Template", {"standard": 1})
	for template in standard_templates:
		doc = stylo.get_doc("Web Template", template.name)
		if not doc.module:
			doc.module = "Website"
			doc.save()
