import stylo


def execute():
	stylo.reload_doc("core", "doctype", "doctype_link")
	stylo.reload_doc("core", "doctype", "doctype_action")
	stylo.reload_doc("core", "doctype", "doctype")
	stylo.model.delete_fields({"DocType": ["hide_heading", "image_view", "read_only_onload"]}, delete=1)

	stylo.db.delete("Property Setter", {"property": "read_only_onload"})
