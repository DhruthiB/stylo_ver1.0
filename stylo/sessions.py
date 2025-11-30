# Copyright (c) 2021, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
"""
Boot session from cache or build

Session bootstraps info needed by common client side activities including
permission, homepage, default variables, system defaults etc
"""
import json
from datetime import datetime, timezone
from urllib.parse import unquote

import redis

import stylo
import stylo.defaults
import stylo.model.meta
import stylo.translate
import stylo.utils
from stylo import _
from stylo.cache_manager import clear_user_cache
from stylo.query_builder import Order
from stylo.utils import cint, cstr, get_assets_json
from stylo.utils.data import add_to_date


@stylo.whitelist()
def clear():
	stylo.local.session_obj.update(force=True)
	stylo.local.db.commit()
	clear_user_cache(stylo.session.user)
	stylo.response["message"] = _("Cache Cleared")


def clear_sessions(user=None, keep_current=False, device=None, force=False):
	"""Clear other sessions of the current user. Called at login / logout

	:param user: user name (default: current user)
	:param keep_current: keep current session (default: false)
	:param device: delete sessions of this device (default: desktop, mobile)
	:param force: triggered by the user (default false)
	"""

	reason = "Logged In From Another Session"
	if force:
		reason = "Force Logged out by the user"

	for sid in get_sessions_to_clear(user, keep_current, device, force):
		delete_session(sid, reason=reason)


def get_sessions_to_clear(user=None, keep_current=False, device=None, force=False):
	"""Returns sessions of the current user. Called at login / logout

	:param user: user name (default: current user)
	:param keep_current: keep current session (default: false)
	:param device: delete sessions of this device (default: desktop, mobile)
	:param force: ignore simultaneous sessions count, log the user out of all except current (default: false)
	"""
	if not user:
		user = stylo.session.user

	if not device:
		device = ("desktop", "mobile")

	if not isinstance(device, tuple | list):
		device = (device,)

	offset = 0
	if not force and user == stylo.session.user:
		simultaneous_sessions = stylo.db.get_value("User", user, "simultaneous_sessions") or 1
		offset = simultaneous_sessions

	session = stylo.qb.DocType("Sessions")
	session_id = stylo.qb.from_(session).where((session.user == user) & (session.device.isin(device)))
	if keep_current:
		if not force:
			offset = max(0, offset - 1)
		session_id = session_id.where(session.sid != stylo.session.sid)

	query = (
		session_id.select(session.sid).offset(offset).limit(100).orderby(session.lastupdate, order=Order.desc)
	)

	return query.run(pluck=True)


def delete_session(sid=None, user=None, reason="Session Expired"):
	from stylo.core.doctype.activity_log.feed import logout_feed

	if stylo.flags.read_only:
		# This isn't manually initiated logout, most likely user's cookies were expired in such case
		# we should just ignore it till database is back up again.
		return

	stylo.cache().hdel("session", sid)
	stylo.cache().hdel("last_db_session_update", sid)
	if sid and not user:
		table = stylo.qb.DocType("Sessions")
		user_details = stylo.qb.from_(table).where(table.sid == sid).select(table.user).run(as_dict=True)
		if user_details:
			user = user_details[0].get("user")

	logout_feed(user, reason)
	stylo.db.delete("Sessions", {"sid": sid})
	stylo.db.commit()


def clear_all_sessions(reason=None):
	"""This effectively logs out all users"""
	stylo.only_for("Administrator")
	if not reason:
		reason = "Deleted All Active Session"
	for sid in stylo.qb.from_("Sessions").select("sid").run(pluck=True):
		delete_session(sid, reason=reason)


def get_expired_sessions():
	"""Returns list of expired sessions"""
	sessions = stylo.qb.DocType("Sessions")
	expired = []
	for device in ("desktop", "mobile"):
		expired.extend(
			(
				stylo.qb.from_(sessions)
				.select(sessions.sid)
				.where((sessions.lastupdate < get_expired_threshold(device)) & (sessions.device == device))
			).run(pluck=True)
		)

	return expired


def clear_expired_sessions():
	"""This function is meant to be called from scheduler"""
	for sid in get_expired_sessions():
		delete_session(sid, reason="Session Expired")


def get():
	"""get session boot info"""
	from stylo.boot import get_bootinfo, get_unseen_notes
	from stylo.utils.change_log import get_change_log

	bootinfo = None
	if not getattr(stylo.conf, "disable_session_cache", None):
		# check if cache exists
		bootinfo = stylo.cache().hget("bootinfo", stylo.session.user)
		if bootinfo:
			bootinfo["from_cache"] = 1
			bootinfo["user"]["recent"] = json.dumps(stylo.cache().hget("user_recent", stylo.session.user))

	if not bootinfo:
		# if not create it
		bootinfo = get_bootinfo()
		stylo.cache().hset("bootinfo", stylo.session.user, bootinfo)
		try:
			stylo.cache().ping()
		except redis.exceptions.ConnectionError:
			message = _("Redis cache server not running. Please contact Administrator / Tech support")
			if "messages" in bootinfo:
				bootinfo["messages"].append(message)
			else:
				bootinfo["messages"] = [message]

		# check only when clear cache is done, and don't cache this
		if stylo.local.request:
			bootinfo["change_log"] = get_change_log()

	bootinfo["metadata_version"] = stylo.cache().get_value("metadata_version")
	if not bootinfo["metadata_version"]:
		bootinfo["metadata_version"] = stylo.reset_metadata_version()

	bootinfo.notes = get_unseen_notes()
	bootinfo.assets_json = get_assets_json()
	bootinfo.read_only = bool(stylo.flags.read_only)

	for hook in stylo.get_hooks("extend_bootinfo"):
		stylo.get_attr(hook)(bootinfo=bootinfo)

	bootinfo["lang"] = stylo.translate.get_user_lang()
	bootinfo["disable_async"] = stylo.conf.disable_async

	bootinfo["setup_complete"] = cint(stylo.get_system_settings("setup_complete"))

	bootinfo["desk_theme"] = stylo.db.get_value("User", stylo.session.user, "desk_theme") or "Light"

	return bootinfo


@stylo.whitelist()
def get_boot_assets_json():
	return get_assets_json()


def get_csrf_token():
	if not stylo.local.session.data.csrf_token:
		generate_csrf_token()

	return stylo.local.session.data.csrf_token


def generate_csrf_token():
	stylo.local.session.data.csrf_token = stylo.generate_hash()
	if not stylo.flags.in_test:
		stylo.local.session_obj.update(force=True)


class Session:
	__slots__ = ("user", "device", "user_type", "full_name", "data", "time_diff", "sid")

	def __init__(
		self,
		user: str,
		resume: bool = False,
		full_name: str | None = None,
		user_type: str | None = None,
		session_end: str | None = None,
		audit_user: str | None = None,
	):
		self.sid = cstr(stylo.form_dict.get("sid") or unquote(stylo.request.cookies.get("sid", "Guest")))
		self.user = user
		self.device = stylo.form_dict.get("device") or "desktop"
		self.user_type = user_type
		self.full_name = full_name
		self.data = stylo._dict({"data": stylo._dict({})})
		self.time_diff = None

		# set local session
		stylo.local.session = self.data

		if resume:
			self.resume()

		else:
			if self.user:
				self.validate_user()
				self.start(session_end, audit_user)

	def validate_user(self):
		if not stylo.get_cached_value("User", self.user, "enabled"):
			stylo.throw(
				_("User {0} is disabled. Please contact your System Manager.").format(self.user),
				stylo.ValidationError,
			)

	def start(self, session_end: str | None = None, audit_user: str | None = None):
		"""start a new session"""
		# generate sid
		if self.user == "Guest":
			sid = "Guest"
		else:
			sid = stylo.generate_hash()

		self.data.user = self.user
		self.sid = self.data.sid = sid
		self.data.data.user = self.user
		self.data.data.session_ip = stylo.local.request_ip

		if session_end:
			self.data.data.session_end = session_end

		if audit_user:
			self.data.data.audit_user = audit_user

		if self.user != "Guest":
			self.data.data.update(
				{
					"last_updated": stylo.utils.now(),
					"session_expiry": get_expiry_period(self.device),
					"creation": stylo.utils.now(),
					"full_name": self.full_name,
					"user_type": self.user_type,
					"device": self.device,
				}
			)

		# insert session
		if self.user != "Guest":
			self.insert_session_record()

			# update user
			user = stylo.get_doc("User", self.data["user"])
			user_doctype = stylo.qb.DocType("User")
			(
				stylo.qb.update(user_doctype)
				.set(user_doctype.last_login, stylo.utils.now())
				.set(user_doctype.last_ip, stylo.local.request_ip)
				.set(user_doctype.last_active, stylo.utils.now())
				.where(user_doctype.name == self.data["user"])
			).run()

			user.run_notifications("before_change")
			user.run_notifications("on_update")
			stylo.db.commit()

	def insert_session_record(self):
		Sessions = stylo.qb.DocType("Sessions")
		now = stylo.utils.now()

		(
			stylo.qb.into(Sessions)
			.columns(
				Sessions.sessiondata,
				Sessions.user,
				Sessions.lastupdate,
				Sessions.sid,
				Sessions.status,
				Sessions.device,
			)
			.insert((str(self.data["data"]), self.data["user"], now, self.data["sid"], "Active", self.device))
		).run()
		stylo.cache().hset("session", self.data.sid, self.data)

	def resume(self):
		"""non-login request: load a session"""
		import stylo
		from stylo.auth import validate_ip_address

		data = self.get_session_record()

		if data:
			self.data.update({"data": data, "user": data.user, "sid": self.sid})
			self.user = data.user
			self.validate_user()
			validate_ip_address(self.user)
			self.device = data.device
		else:
			self.start_as_guest()

		if self.sid != "Guest":
			stylo.local.user_lang = stylo.translate.get_user_lang(self.data.user)
			stylo.local.lang = stylo.local.user_lang

	def get_session_record(self):
		"""get session record, or return the standard Guest Record"""
		from stylo.auth import clear_cookies

		r = self.get_session_data()

		if not r:
			stylo.response["session_expired"] = 1
			clear_cookies()
			self.sid = "Guest"
			r = self.get_session_data()

		return r

	def get_session_data(self):
		if self.sid == "Guest":
			return stylo._dict({"user": "Guest"})

		data = self.get_session_data_from_cache()
		if not data:
			data = self.get_session_data_from_db()
		return data

	def get_session_data_from_cache(self):
		data = stylo.cache().hget("session", self.sid)
		if data:
			data = stylo._dict(data)
			session_data = data.get("data", {})

			# set user for correct timezone
			self.time_diff = stylo.utils.time_diff_in_seconds(
				stylo.utils.now(), session_data.get("last_updated")
			)
			expiry = get_expiry_in_seconds(session_data.get("session_expiry"))

			if self.time_diff > expiry or (
				(session_end := session_data.get("session_end"))
				and datetime.now(tz=timezone.utc) > datetime.fromisoformat(session_end)
			):
				self._delete_session()
				data = None

		return data and data.data

	def get_session_data_from_db(self):
		sessions = stylo.qb.DocType("Sessions")

		self.device = (
			stylo.db.get_value(
				sessions,
				filters=sessions.sid == self.sid,
				fieldname="device",
				order_by=None,
			)
			or "desktop"
		)

		record = (
			stylo.qb.from_(sessions)
			.select(sessions.user, sessions.sessiondata)
			.where(sessions.sid == self.sid)
			.where(sessions.lastupdate > get_expired_threshold(self.device))
		).run()

		if record:
			data = stylo._dict(stylo.safe_eval(record and record[0][1] or "{}"))
			data.user = record[0][0]
		else:
			self._delete_session()
			data = None

		return data

	def _delete_session(self):
		delete_session(self.sid, reason="Session Expired")

	def start_as_guest(self):
		"""all guests share the same 'Guest' session"""
		self.user = "Guest"
		self.start()

	def update(self, force=False):
		"""extend session expiry"""
		if stylo.session["user"] == "Guest" or stylo.form_dict.cmd == "logout":
			return

		now = stylo.utils.now()

		Sessions = stylo.qb.DocType("Sessions")

		self.data["data"]["last_updated"] = now
		self.data["data"]["lang"] = str(stylo.lang)

		# update session in db
		last_updated = stylo.cache().hget("last_db_session_update", self.sid)
		time_diff = stylo.utils.time_diff_in_seconds(now, last_updated) if last_updated else None

		# database persistence is secondary, don't update it too often
		updated_in_db = False
		if (force or (time_diff is None) or (time_diff > 600)) and not stylo.flags.read_only:
			# update sessions table
			(
				stylo.qb.update(Sessions)
				.where(Sessions.sid == self.data["sid"])
				.set(Sessions.sessiondata, str(self.data["data"]))
				.set(Sessions.lastupdate, now)
			).run()

			stylo.db.set_value("User", stylo.session.user, "last_active", now, update_modified=False)

			stylo.db.commit()
			stylo.cache().hset("last_db_session_update", self.sid, now)

			updated_in_db = True

		stylo.cache().hset("session", self.sid, self.data)

		return updated_in_db


def get_expiry_period_for_query(device=None):
	if stylo.db.db_type == "postgres":
		return get_expiry_period(device)
	else:
		return get_expiry_in_seconds(device=device)


def get_expiry_in_seconds(expiry=None, device=None):
	if not expiry:
		expiry = get_expiry_period(device)
	parts = expiry.split(":")
	return (cint(parts[0]) * 3600) + (cint(parts[1]) * 60) + cint(parts[2])


def get_expired_threshold(device):
	"""Get cutoff time before which all sessions are considered expired."""

	now = stylo.utils.now()
	expiry_in_seconds = get_expiry_in_seconds(device=device)

	return add_to_date(now, seconds=-expiry_in_seconds, as_string=True)


def get_expiry_period(device="desktop"):
	if device == "mobile":
		key = "session_expiry_mobile"
		default = "720:00:00"
	else:
		key = "session_expiry"
		default = "06:00:00"

	exp_sec = stylo.defaults.get_global_default(key) or default

	# incase seconds is missing
	if len(exp_sec.split(":")) == 2:
		exp_sec = exp_sec + ":00"

	return exp_sec


def get_geo_from_ip(ip_addr):
	try:
		from geolite2 import geolite2

		with geolite2 as f:
			reader = f.reader()
			data = reader.get(ip_addr)

			return stylo._dict(data)
	except ImportError:
		return
	except ValueError:
		return
	except TypeError:
		return


def get_geo_ip_country(ip_addr):
	match = get_geo_from_ip(ip_addr)
	if match:
		return match.country
