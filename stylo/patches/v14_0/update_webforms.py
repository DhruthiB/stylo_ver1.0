# Copyright (c) 2021, Stylo Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import stylo


def execute():
	stylo.reload_doc("website", "doctype", "web_form_list_column")
	stylo.reload_doctype("Web Form")

	for web_form in stylo.get_all("Web Form", fields=["*"]):
		if web_form.allow_multiple and not web_form.show_list:
			stylo.db.set_value("Web Form", web_form.name, "show_list", True)
