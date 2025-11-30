# Copyright (c) 2022, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import datetime
import decimal
import json
import mimetypes
import os
from typing import TYPE_CHECKING
from urllib.parse import quote

import werkzeug.utils
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.local import LocalProxy
from werkzeug.wrappers import Response
from werkzeug.wsgi import wrap_file

import stylo
import stylo.model.document
import stylo.sessions
import stylo.utils
from stylo import _
from stylo.core.doctype.access_log.access_log import make_access_log
from stylo.utils import cint, format_timedelta

if TYPE_CHECKING:
	from stylo.core.doctype.file.file import File


def report_error(status_code):
	"""Build error. Show traceback in developer mode"""
	allow_traceback = is_traceback_allowed() and (status_code != 404 or stylo.conf.logging)

	if allow_traceback:
		traceback = stylo.utils.get_traceback()
		if traceback:
			stylo.errprint(traceback)
			stylo.local.response.exception = traceback.splitlines()[-1]

	response = build_response("json")
	response.status_code = status_code
	return response


def is_traceback_allowed():
	return (
		stylo.db
		and stylo.get_system_settings("allow_error_traceback")
		and (not stylo.local.flags.disable_traceback or stylo._dev_server)
	)


def build_response(response_type=None):
	if "docs" in stylo.local.response and not stylo.local.response.docs:
		del stylo.local.response["docs"]

	response_type_map = {
		"csv": as_csv,
		"txt": as_txt,
		"download": as_raw,
		"json": as_json,
		"pdf": as_pdf,
		"page": as_page,
		"redirect": redirect,
		"binary": as_binary,
	}

	return response_type_map[stylo.response.get("type") or response_type]()


def as_csv():
	response = Response()
	response.mimetype = "text/csv"
	filename = f"{stylo.response['doctype']}.csv"
	filename = filename.encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", "attachment", filename=filename)
	response.data = stylo.response["result"]
	return response


def as_txt():
	response = Response()
	response.mimetype = "text"
	filename = f"{stylo.response['doctype']}.txt"
	filename = filename.encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", "attachment", filename=filename)
	response.data = stylo.response["result"]
	return response


def as_raw():
	response = Response()
	response.mimetype = (
		stylo.response.get("content_type")
		or mimetypes.guess_type(stylo.response["filename"])[0]
		or "application/unknown"
	)
	filename = stylo.response["filename"].encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add(
		"Content-Disposition",
		stylo.response.get("display_content_as", "attachment"),
		filename=filename,
	)
	response.data = stylo.response["filecontent"]
	return response


def as_json():
	make_logs()
	response = Response()
	if stylo.local.response.http_status_code:
		response.status_code = stylo.local.response["http_status_code"]
		del stylo.local.response["http_status_code"]

	response.mimetype = "application/json"
	response.data = json.dumps(stylo.local.response, default=json_handler, separators=(",", ":"))
	return response


def as_pdf():
	response = Response()
	response.mimetype = "application/pdf"
	filename = stylo.response["filename"].encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", None, filename=filename)
	response.data = stylo.response["filecontent"]
	return response


def as_binary():
	response = Response()
	response.mimetype = "application/octet-stream"
	filename = stylo.response["filename"]
	filename = filename.encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", None, filename=filename)
	response.data = stylo.response["filecontent"]
	return response


def make_logs(response=None):
	"""make strings for msgprint and errprint"""
	if not response:
		response = stylo.local.response

	if stylo.error_log and is_traceback_allowed():
		response["exc"] = json.dumps([stylo.utils.cstr(d["exc"]) for d in stylo.local.error_log])

	if stylo.local.message_log:
		response["_server_messages"] = json.dumps([stylo.utils.cstr(d) for d in stylo.local.message_log])

	if stylo.debug_log and stylo.conf.get("logging") or False:
		response["_debug_messages"] = json.dumps(stylo.local.debug_log)

	if stylo.flags.error_message:
		response["_error_message"] = stylo.flags.error_message


def json_handler(obj):
	"""serialize non-serializable data for json"""
	from collections.abc import Iterable
	from re import Match

	if isinstance(obj, datetime.date | datetime.datetime | datetime.time):
		return str(obj)

	elif isinstance(obj, datetime.timedelta):
		return format_timedelta(obj)

	elif isinstance(obj, decimal.Decimal):
		return float(obj)

	elif isinstance(obj, LocalProxy):
		return str(obj)

	elif isinstance(obj, stylo.model.document.BaseDocument):
		doc = obj.as_dict(no_nulls=True)
		return doc

	elif isinstance(obj, Iterable):
		return list(obj)

	elif isinstance(obj, Match):
		return obj.string

	elif type(obj) == type or isinstance(obj, Exception):
		return repr(obj)

	elif callable(obj):
		return repr(obj)

	else:
		raise TypeError(f"""Object of type {type(obj)} with value of {obj!r} is not JSON serializable""")


def as_page():
	"""print web page"""
	from stylo.website.serve import get_response

	return get_response(stylo.response["route"], http_status_code=stylo.response.get("http_status_code"))


def redirect():
	return werkzeug.utils.redirect(stylo.response.location)


def download_backup(path):
	try:
		stylo.only_for(("System Manager", "Administrator"))
		make_access_log(report_name="Backup")
	except stylo.PermissionError:
		raise Forbidden(
			_("You need to be logged in and have System Manager Role to be able to access backups.")
		)

	return send_private_file(path)


def download_private_file(path: str) -> Response:
	"""Checks permissions and sends back private file"""
	from stylo.core.doctype.file.utils import find_file_by_url

	if stylo.session.user == "Guest":
		raise Forbidden(_("You don't have permission to access this file"))

	file = find_file_by_url(path, name=stylo.form_dict.fid)
	if not file:
		raise Forbidden(_("You don't have permission to access this file"))

	make_access_log(doctype="File", document=file.name, file_type=os.path.splitext(path)[-1][1:])
	return send_private_file(path.split("/private", 1)[1])


def send_private_file(path: str) -> Response:
	path = os.path.join(stylo.local.conf.get("private_path", "private"), path.strip("/"))
	filename = os.path.basename(path)

	if stylo.local.request.headers.get("X-Use-X-Accel-Redirect"):
		path = "/protected/" + path
		response = Response()
		response.headers["X-Accel-Redirect"] = quote(stylo.utils.encode(path))

	else:
		filepath = stylo.utils.get_site_path(path)
		try:
			f = open(filepath, "rb")
		except OSError:
			raise NotFound

		response = Response(wrap_file(stylo.local.request.environ, f), direct_passthrough=True)

	# no need for content disposition and force download. let browser handle its opening.
	# Except for those that can be injected with scripts.

	extension = os.path.splitext(path)[1]
	blacklist = [".svg", ".html", ".htm", ".xml"]

	if extension.lower() in blacklist:
		response.headers.add("Content-Disposition", "attachment", filename=filename)

	response.mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"

	return response


def handle_session_stopped():
	from stylo.website.serve import get_response

	stylo.respond_as_web_page(
		_("Updating"),
		_("The system is being updated. Please refresh again after a few moments."),
		http_status_code=503,
		indicator_color="orange",
		fullpage=True,
		primary_action=None,
	)
	return get_response("message", http_status_code=503)
