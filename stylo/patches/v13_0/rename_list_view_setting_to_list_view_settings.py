# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	if not stylo.db.table_exists("List View Setting"):
		return
	if not stylo.db.exists("DocType", "List View Setting"):
		return

	stylo.reload_doc("desk", "doctype", "List View Settings")

	existing_list_view_settings = stylo.get_all("List View Settings", as_list=True, order_by="modified")
	for list_view_setting in stylo.get_all(
		"List View Setting",
		fields=["disable_count", "disable_sidebar_stats", "disable_auto_refresh", "name"],
		order_by="modified",
	):
		name = list_view_setting.pop("name")
		if name not in [x[0] for x in existing_list_view_settings]:
			list_view_setting["doctype"] = "List View Settings"
			list_view_settings = stylo.get_doc(list_view_setting)
			# setting name here is necessary because autoname is set as prompt
			list_view_settings.name = name
			list_view_settings.insert()

	stylo.delete_doc("DocType", "List View Setting", force=True)
