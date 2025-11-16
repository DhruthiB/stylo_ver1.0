# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import stylo


def add_custom_field(doctype, fieldname, fieldtype="Data", options=None):
	stylo.get_doc(
		{
			"doctype": "Custom Field",
			"dt": doctype,
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"options": options,
		}
	).insert()


def clear_custom_fields(doctype):
	stylo.db.delete("Custom Field", {"dt": doctype})
	stylo.clear_cache(doctype=doctype)
