import json

from werkzeug.routing import Rule

import stylo
from stylo import _
from stylo.utils import attach_expanded_links
from stylo.utils.data import sbool


def document_list(doctype: str):
	if stylo.form_dict.get("fields"):
		stylo.form_dict["fields"] = json.loads(stylo.form_dict["fields"])

	if stylo.form_dict.get("expand"):
		stylo.form_dict["expand"] = json.loads(stylo.form_dict["expand"])

	# set limit of records for stylo.get_list
	stylo.form_dict.setdefault(
		"limit_page_length",
		stylo.form_dict.limit or stylo.form_dict.limit_page_length or 20,
	)

	# convert strings to native types - only as_dict and debug accept bool
	for param in ["as_dict", "debug"]:
		param_val = stylo.form_dict.get(param)
		if param_val is not None:
			stylo.form_dict[param] = sbool(param_val)

	# evaluate stylo.get_list
	return stylo.call(stylo.client.get_list, doctype, **stylo.form_dict)


def handle_rpc_call(method: str):
	import stylo.handler

	method = method.split("/")[0]  # for backward compatiblity

	stylo.form_dict.cmd = method
	return stylo.handler.handle()


def create_doc(doctype: str):
	data = get_request_form_data()
	data.pop("doctype", None)
	return stylo.new_doc(doctype, **data).insert()


def update_doc(doctype: str, name: str):
	data = get_request_form_data()

	doc = stylo.get_doc(doctype, name, for_update=True)
	if "flags" in data:
		del data["flags"]

	doc.update(data)
	doc.save()

	# check for child table doctype
	if doc.get("parenttype"):
		stylo.get_doc(doc.parenttype, doc.parent).save()

	return doc


def delete_doc(doctype: str, name: str):
	# TODO: child doc handling
	stylo.delete_doc(doctype, name, ignore_missing=False)
	stylo.response.http_status_code = 202
	return "ok"


def read_doc(doctype: str, name: str):
	# Backward compatiblity
	if "run_method" in stylo.form_dict:
		return execute_doc_method(doctype, name)

	doc = stylo.get_doc(doctype, name)
	doc.check_permission("read")
	doc.apply_fieldlevel_read_permissions()
	if sbool(stylo.form_dict.get("expand_links")):
		doc_dict = doc.as_dict()
		get_values_for_link_and_dynamic_link_fields(doc_dict)
		get_values_for_table_and_multiselect_fields(doc_dict)
		return doc_dict

	return doc


def get_values_for_link_and_dynamic_link_fields(doc_dict):
	meta = stylo.get_meta(doc_dict.doctype)
	link_fields = meta.get_link_fields() + meta.get_dynamic_link_fields()

	for field in link_fields:
		if not (doc_fieldvalue := getattr(doc_dict, field.fieldname, None)):
			continue

		doctype = field.options if field.fieldtype == "Link" else doc_dict.get(field.options)

		link_doc = stylo.get_doc(doctype, doc_fieldvalue)
		doc_dict.update({field.fieldname: link_doc})


def get_values_for_table_and_multiselect_fields(doc_dict):
	meta = stylo.get_meta(doc_dict.doctype)
	table_fields = meta.get_table_fields()

	for field in table_fields:
		table_link_fieldnames = [f.fieldname for f in stylo.get_meta(field.options).get_link_fields()]
		attach_expanded_links(field.options, doc_dict.get(field.fieldname), table_link_fieldnames)


def execute_doc_method(doctype: str, name: str, method: str | None = None):
	method = method or stylo.form_dict.pop("run_method")
	doc = stylo.get_doc(doctype, name)
	doc.is_whitelisted(method)

	if stylo.request.method == "GET":
		doc.check_permission("read")
		return doc.run_method(method, **stylo.form_dict)

	elif stylo.request.method == "POST":
		doc.check_permission("write")
		return doc.run_method(method, **stylo.form_dict)


def get_request_form_data():
	if stylo.form_dict.data is None:
		data = stylo.safe_decode(stylo.request.get_data())
	else:
		data = stylo.form_dict.data

	try:
		return stylo.parse_json(data)
	except ValueError:
		return stylo.form_dict


url_rules = [
	Rule("/method/<path:method>", endpoint=handle_rpc_call),
	Rule("/resource/<doctype>", methods=["GET"], endpoint=document_list),
	Rule("/resource/<doctype>", methods=["POST"], endpoint=create_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["GET"], endpoint=read_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["PUT"], endpoint=update_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["DELETE"], endpoint=delete_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["POST"], endpoint=execute_doc_method),
]
