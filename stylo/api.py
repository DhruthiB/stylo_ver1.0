# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import base64
import binascii
import json
from urllib.parse import urlencode, urlparse

import stylo
import stylo.client
import stylo.handler
from stylo import _
from stylo.utils.data import sbool
from stylo.utils.password import get_decrypted_password
from stylo.utils.response import build_response


def handle():
	"""
	Handler for `/api` methods

	### Examples:

	`/api/method/{methodname}` will call a whitelisted method

	`/api/resource/{doctype}` will query a table
	        examples:
	        - `?fields=["name", "owner"]`
	        - `?filters=[["Task", "name", "like", "%005"]]`
	        - `?limit_start=0`
	        - `?limit_page_length=20`

	`/api/resource/{doctype}/{name}` will point to a resource
	        `GET` will return doclist
	        `POST` will insert
	        `PUT` will update
	        `DELETE` will delete

	`/api/resource/{doctype}/{name}?run_method={method}` will run a whitelisted controller method
	"""

	parts = stylo.request.path[1:].split("/", 3)
	call = doctype = name = None

	if len(parts) > 1:
		call = parts[1]

	if len(parts) > 2:
		doctype = parts[2]

	if len(parts) > 3:
		name = parts[3]

	if call == "method":
		stylo.local.form_dict.cmd = doctype
		return stylo.handler.handle()

	elif call == "resource":
		if "run_method" in stylo.local.form_dict:
			method = stylo.local.form_dict.pop("run_method")
			doc = stylo.get_doc(doctype, name)
			doc.is_whitelisted(method)

			if stylo.local.request.method == "GET":
				if not doc.has_permission("read"):
					stylo.throw(_("Not permitted"), stylo.PermissionError)
				stylo.local.response.update({"data": doc.run_method(method, **stylo.local.form_dict)})

			if stylo.local.request.method == "POST":
				if not doc.has_permission("write"):
					stylo.throw(_("Not permitted"), stylo.PermissionError)

				stylo.local.response.update({"data": doc.run_method(method, **stylo.local.form_dict)})
				stylo.db.commit()

		else:
			if name:
				if stylo.local.request.method == "GET":
					doc = stylo.get_doc(doctype, name)
					if not doc.has_permission("read"):
						raise stylo.PermissionError
					if stylo.get_system_settings("apply_perm_level_on_api_calls"):
						doc.apply_fieldlevel_read_permissions()
					stylo.local.response.update({"data": doc})

				if stylo.local.request.method == "PUT":
					data = get_request_form_data()

					doc = stylo.get_doc(doctype, name, for_update=True)

					if "flags" in data:
						del data["flags"]

					# Not checking permissions here because it's checked in doc.save
					doc.update(data)
					doc.save()
					if stylo.get_system_settings("apply_perm_level_on_api_calls"):
						doc.apply_fieldlevel_read_permissions()
					stylo.local.response.update({"data": doc})

					# check for child table doctype
					if doc.get("parenttype"):
						stylo.get_doc(doc.parenttype, doc.parent).save()

					stylo.db.commit()

				if stylo.local.request.method == "DELETE":
					# Not checking permissions here because it's checked in delete_doc
					stylo.delete_doc(doctype, name, ignore_missing=False)
					stylo.local.response.http_status_code = 202
					stylo.local.response.message = "ok"
					stylo.db.commit()

			elif doctype:
				if stylo.local.request.method == "GET":
					# set fields for stylo.get_list
					if stylo.local.form_dict.get("fields"):
						stylo.local.form_dict["fields"] = json.loads(stylo.local.form_dict["fields"])

					# set limit of records for stylo.get_list
					stylo.local.form_dict.setdefault(
						"limit_page_length",
						stylo.local.form_dict.limit or stylo.local.form_dict.limit_page_length or 20,
					)

					# convert strings to native types - only as_dict and debug accept bool
					for param in ["as_dict", "debug"]:
						param_val = stylo.local.form_dict.get(param)
						if param_val is not None:
							stylo.local.form_dict[param] = sbool(param_val)

					# evaluate stylo.get_list
					data = stylo.call(stylo.client.get_list, doctype, **stylo.local.form_dict)

					# set stylo.get_list result to response
					stylo.local.response.update({"data": data})

				if stylo.local.request.method == "POST":
					# fetch data from from dict
					data = get_request_form_data()
					data.update({"doctype": doctype})

					# insert document from request data
					doc = stylo.get_doc(data).insert()

					# set response data
					stylo.local.response.update({"data": doc.as_dict()})

					# commit for POST requests
					stylo.db.commit()
			else:
				raise stylo.DoesNotExistError

	else:
		raise stylo.DoesNotExistError

	return build_response("json")


def get_request_form_data():
	if stylo.local.form_dict.data is None:
		data = stylo.safe_decode(stylo.local.request.get_data())
	else:
		data = stylo.local.form_dict.data

	try:
		return stylo.parse_json(data)
	except ValueError:
		return stylo.local.form_dict


def validate_auth():
	"""
	Authenticate and sets user for the request.
	"""
	authorization_header = stylo.get_request_header("Authorization", "").split(" ")

	if len(authorization_header) == 2:
		validate_oauth(authorization_header)
		validate_auth_via_api_keys(authorization_header)

	validate_auth_via_hooks()

	# If login via bearer, basic or keypair didn't work then authentication failed and we
	# should terminate here.
	if len(authorization_header) == 2 and stylo.session.user in ("", "Guest"):
		raise stylo.AuthenticationError


def validate_oauth(authorization_header):
	"""
	Authenticate request using OAuth and set session user

	Args:
	        authorization_header (list of str): The 'Authorization' header containing the prefix and token
	"""

	from stylo.integrations.oauth2 import get_oauth_server
	from stylo.oauth import get_url_delimiter

	if authorization_header[0].lower() != "bearer":
		return

	form_dict = stylo.local.form_dict
	token = authorization_header[1]
	req = stylo.request
	parsed_url = urlparse(req.url)
	access_token = {"access_token": token}
	uri = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path + "?" + urlencode(access_token)
	http_method = req.method
	headers = req.headers
	body = req.get_data()
	if req.content_type and "multipart/form-data" in req.content_type:
		body = None

	try:
		required_scopes = stylo.db.get_value("OAuth Bearer Token", token, "scopes").split(
			get_url_delimiter()
		)
		valid, oauthlib_request = get_oauth_server().verify_request(
			uri, http_method, body, headers, required_scopes
		)
		if valid:
			stylo.set_user(stylo.db.get_value("OAuth Bearer Token", token, "user"))
			stylo.local.form_dict = form_dict
	except AttributeError:
		pass


def validate_auth_via_api_keys(authorization_header):
	"""
	Authenticate request using API keys and set session user

	Args:
	        authorization_header (list of str): The 'Authorization' header containing the prefix and token
	"""

	try:
		auth_type, auth_token = authorization_header
		authorization_source = stylo.get_request_header("Stylo-Authorization-Source")
		if auth_type.lower() == "basic":
			api_key, api_secret = stylo.safe_decode(base64.b64decode(auth_token)).split(":")
			validate_api_key_secret(api_key, api_secret, authorization_source)
		elif auth_type.lower() == "token":
			api_key, api_secret = auth_token.split(":")
			validate_api_key_secret(api_key, api_secret, authorization_source)
	except binascii.Error:
		stylo.throw(
			_("Failed to decode token, please provide a valid base64-encoded token."),
			stylo.InvalidAuthorizationToken,
		)
	except (AttributeError, TypeError, ValueError):
		pass


def validate_api_key_secret(api_key, api_secret, stylo_authorization_source=None):
	"""stylo_authorization_source to provide api key and secret for a doctype apart from User"""
	doctype = stylo_authorization_source or "User"
	doc = stylo.db.get_value(doctype=doctype, filters={"api_key": api_key}, fieldname=["name"])
	if not doc:
		raise stylo.AuthenticationError
	form_dict = stylo.local.form_dict
	doc_secret = get_decrypted_password(doctype, doc, fieldname="api_secret", raise_exception=False)
	if doc_secret and api_secret == doc_secret:
		if doctype == "User":
			user = stylo.db.get_value(doctype="User", filters={"api_key": api_key}, fieldname=["name"])
		else:
			user = stylo.db.get_value(doctype, doc, "user")
		if stylo.local.login_manager.user in ("", "Guest"):
			stylo.set_user(user)
		stylo.local.form_dict = form_dict
	else:
		raise stylo.AuthenticationError


def validate_auth_via_hooks():
	for auth_hook in stylo.get_hooks("auth_hooks", []):
		stylo.get_attr(auth_hook)()
