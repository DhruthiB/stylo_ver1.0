# Copyright (c) 2022, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import os
from mimetypes import guess_type
from typing import TYPE_CHECKING

from werkzeug.wrappers import Response

import stylo
import stylo.sessions
import stylo.utils
from stylo import _, is_whitelisted
from stylo.core.doctype.file.utils import find_file_by_url
from stylo.core.doctype.server_script.server_script_utils import get_server_script_map
from stylo.monitor import add_data_to_monitor
from stylo.permissions import check_doctype_permission
from stylo.utils import cint
from stylo.utils.csvutils import build_csv_response
from stylo.utils.image import optimize_image
from stylo.utils.response import build_response

if TYPE_CHECKING:
	from stylo.core.doctype.file.file import File
	from stylo.core.doctype.user.user import User

ALLOWED_MIMETYPES = (
	"image/png",
	"image/jpeg",
	"application/pdf",
	"application/msword",
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	"application/vnd.ms-excel",
	"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	"application/vnd.oasis.opendocument.text",
	"application/vnd.oasis.opendocument.spreadsheet",
	"text/plain",
	"video/quicktime",
	"video/mp4",
)


def handle():
	"""handle request"""

	cmd = stylo.local.form_dict.cmd
	data = None

	if cmd != "login":
		data = execute_cmd(cmd)

	# data can be an empty string or list which are valid responses
	if data is not None:
		if isinstance(data, Response):
			# method returns a response object, pass it on
			return data

		# add the response to `message` label
		stylo.response["message"] = data

	return build_response("json")


def execute_cmd(cmd, from_async=False):
	"""execute a request as python module"""
	cmd = stylo.override_whitelisted_method(cmd)

	# via server script
	server_script = get_server_script_map().get("_api", {}).get(cmd)
	if server_script:
		return run_server_script(server_script)

	try:
		method = get_attr(cmd)
	except Exception as e:
		stylo.throw(_("Failed to get method for command {0} with {1}").format(cmd, e))

	if from_async:
		method = method.queue

	if method != run_doc_method:
		is_whitelisted(method)
		is_valid_http_method(method)

	return stylo.call(method, **stylo.form_dict)


def run_server_script(server_script):
	response = stylo.get_doc("Server Script", server_script).execute_method()

	# some server scripts return output using flags (empty dict by default),
	# while others directly modify stylo.response
	# return flags if not empty dict (this overwrites stylo.response.message)
	if response != {}:
		return response


def is_valid_http_method(method):
	if stylo.flags.in_safe_exec:
		return

	http_method = stylo.local.request.method

	if http_method not in stylo.allowed_http_methods_for_whitelisted_func[method]:
		throw_permission_error()


def throw_permission_error():
	stylo.throw(_("Not permitted"), stylo.PermissionError)


@stylo.whitelist(allow_guest=True)
def logout():
	stylo.local.login_manager.logout()
	stylo.db.commit()


@stylo.whitelist(allow_guest=True)
def web_logout():
	stylo.local.login_manager.logout()
	stylo.db.commit()
	stylo.respond_as_web_page(
		_("Logged Out"), _("You have been successfully logged out"), indicator_color="green"
	)


@stylo.whitelist()
def uploadfile():
	ret = None
	check_write_permission(stylo.form_dict.doctype, stylo.form_dict.docname)

	try:
		if stylo.form_dict.get("from_form"):
			try:
				ret = stylo.get_doc(
					{
						"doctype": "File",
						"attached_to_name": stylo.form_dict.docname,
						"attached_to_doctype": stylo.form_dict.doctype,
						"attached_to_field": stylo.form_dict.docfield,
						"file_url": stylo.form_dict.file_url,
						"file_name": stylo.form_dict.filename,
						"is_private": stylo.utils.cint(stylo.form_dict.is_private),
						"content": stylo.form_dict.filedata,
						"decode": True,
					}
				)
				ret.save()
			except stylo.DuplicateEntryError:
				# ignore pass
				ret = None
				stylo.db.rollback()
		else:
			if stylo.form_dict.get("method"):
				method = stylo.get_attr(stylo.form_dict.method)
				is_whitelisted(method)
				ret = method()
	except Exception:
		stylo.errprint(stylo.utils.get_traceback())
		stylo.response["http_status_code"] = 500
		ret = None

	return ret


@stylo.whitelist(allow_guest=True)
def upload_file():
	user = None
	if stylo.session.user == "Guest":
		if stylo.get_system_settings("allow_guests_to_upload_files"):
			ignore_permissions = True
		else:
			raise stylo.PermissionError
	else:
		user: "User" = stylo.get_doc("User", stylo.session.user)
		ignore_permissions = False

	files = stylo.request.files
	is_private = stylo.form_dict.is_private
	doctype = stylo.form_dict.doctype
	docname = stylo.form_dict.docname
	fieldname = stylo.form_dict.fieldname
	file_url = stylo.form_dict.file_url
	folder = stylo.form_dict.folder or "Home"
	method = stylo.form_dict.method
	filename = stylo.form_dict.file_name
	optimize = stylo.form_dict.optimize
	content = None

	if not ignore_permissions:
		check_write_permission(doctype, docname)

	if library_file := stylo.form_dict.get("library_file_name"):
		stylo.has_permission("File", doc=library_file, throw=True)
		doc = stylo.get_value(
			"File",
			stylo.form_dict.library_file_name,
			["is_private", "file_url", "file_name"],
			as_dict=True,
		)
		is_private = doc.is_private
		file_url = doc.file_url
		filename = doc.file_name

	if "file" in files:
		file = files["file"]
		content = file.stream.read()
		filename = file.filename

		content_type = guess_type(filename)[0]
		if optimize and content_type and content_type.startswith("image/"):
			args = {"content": content, "content_type": content_type}
			if stylo.form_dict.max_width:
				args["max_width"] = int(stylo.form_dict.max_width)
			if stylo.form_dict.max_height:
				args["max_height"] = int(stylo.form_dict.max_height)
			content = optimize_image(**args)

	stylo.local.uploaded_file_url = file_url
	stylo.local.uploaded_file = content
	stylo.local.uploaded_filename = filename

	if content is not None and (stylo.session.user == "Guest" or (user and not user.has_desk_access())):
		filetype = guess_type(filename)[0]
		if filetype not in ALLOWED_MIMETYPES:
			stylo.throw(_("You can only upload JPG, PNG, PDF, TXT or Microsoft documents."))

	if method:
		method = stylo.get_attr(method)
		is_whitelisted(method)
		return method()
	else:
		return stylo.get_doc(
			{
				"doctype": "File",
				"attached_to_doctype": doctype,
				"attached_to_name": docname,
				"attached_to_field": fieldname,
				"folder": folder,
				"file_name": filename,
				"file_url": file_url,
				"is_private": cint(is_private),
				"content": content,
			}
		).save(ignore_permissions=ignore_permissions)


def check_write_permission(doctype: str | None = None, name: str | None = None):
	if not doctype:
		return

	if not name:
		stylo.has_permission(doctype, "write", throw=True)
		return

	try:
		doc = stylo.get_doc(doctype, name)
	except stylo.DoesNotExistError:
		# doc has not been inserted yet, name is set to "new-some-doctype"
		# If doc inserts fine then only this attachment will be linked see file/utils.py:relink_mismatched_files
		stylo.new_doc(doctype).check_permission("write")
		return

	doc.check_permission("write")


@stylo.whitelist(allow_guest=True)
def download_file(file_url: str):
	"""
	Download file using token and REST API. Valid session or
	token is required to download private files.

	Method : GET
	Endpoints : download_file, stylo.core.doctype.file.file.download_file
	URL Params : file_name = /path/to/file relative to site path
	"""
	file = find_file_by_url(file_url)
	if not file:
		raise stylo.PermissionError

	stylo.local.response.filename = os.path.basename(file_url)
	stylo.local.response.filecontent = file.get_content()
	stylo.local.response.type = "download"


def get_attr(cmd):
	"""get method object from cmd"""
	if "." in cmd:
		method = stylo.get_attr(cmd)
	else:
		method = globals()[cmd]
	stylo.log("method:" + cmd)
	return method


@stylo.whitelist(allow_guest=True)
def ping():
	return "pong"


def run_doc_method(method, docs=None, dt=None, dn=None, arg=None, args=None):
	"""run a whitelisted controller method"""
	from inspect import getfullargspec

	if not args and arg:
		args = arg

	if dt:  # not called from a doctype (from a page)
		if not dn:
			dn = dt  # single
		doc = stylo.get_doc(dt, dn)

	else:
		docs = stylo.parse_json(docs)
		doc = stylo.get_doc(docs)
		doc._original_modified = doc.modified
		doc.check_if_latest()

	if not doc or not doc.has_permission("read"):
		throw_permission_error()

	try:
		args = stylo.parse_json(args)
	except ValueError:
		pass

	method_obj = getattr(doc, method)
	fn = getattr(method_obj, "__func__", method_obj)
	is_whitelisted(fn)
	is_valid_http_method(fn)

	fnargs = getfullargspec(method_obj).args

	if not fnargs or (len(fnargs) == 1 and fnargs[0] == "self"):
		response = doc.run_method(method)

	elif "args" in fnargs or not isinstance(args, dict):
		response = doc.run_method(method, args)

	else:
		response = doc.run_method(method, **args)

	stylo.response.docs.append(doc)
	if response is None:
		return

	# build output as csv
	if cint(stylo.form_dict.get("as_csv")):
		build_csv_response(response, _(doc.doctype).replace(" ", ""))
		return

	stylo.response["message"] = response

	add_data_to_monitor(methodname=method)


# for backwards compatibility
runserverobj = run_doc_method
