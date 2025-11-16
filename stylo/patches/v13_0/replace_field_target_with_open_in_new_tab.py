import stylo


def execute():
	doctype = "Top Bar Item"
	if not stylo.db.table_exists(doctype) or not stylo.db.has_column(doctype, "target"):
		return

	stylo.reload_doc("website", "doctype", "top_bar_item")
	stylo.db.set_value(doctype, {"target": 'target = "_blank"'}, "open_in_new_tab", 1)
