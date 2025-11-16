# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os

no_cache = 1

import json
import re
from urllib.parse import urlencode

import stylo
import stylo.sessions
from stylo import _
from stylo.utils.jinja_globals import is_rtl

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
	if stylo.session.user == "Guest":
		stylo.response["status_code"] = 403
		stylo.msgprint(_("Log in to access this page."))
		stylo.redirect(f"/login?{urlencode({'redirect-to': stylo.request.path})}")

	elif stylo.session.data.user_type == "Website User":
		stylo.throw(_("You are not permitted to access this page."), stylo.PermissionError)

	try:
		boot = stylo.sessions.get()
	except Exception as e:
		raise stylo.SessionBootFailed from e

	# this needs commit
	csrf_token = stylo.sessions.get_csrf_token()

	stylo.db.commit()

	hooks = stylo.get_hooks()
	app_include_js = hooks.get("app_include_js", []) + stylo.conf.get("app_include_js", [])
	app_include_css = hooks.get("app_include_css", []) + stylo.conf.get("app_include_css", [])
	app_include_icons = hooks.get("app_include_icons", [])

	if stylo.get_system_settings("enable_telemetry") and os.getenv("FRAPPE_SENTRY_DSN"):
		app_include_js.append("sentry.bundle.js")

	context.update(
		{
			"no_cache": 1,
			"build_version": stylo.utils.get_build_version(),
			"app_include_js": app_include_js,
			"app_include_css": app_include_css,
			"app_include_icons": app_include_icons,
			"layout_direction": "rtl" if is_rtl() else "ltr",
			"lang": stylo.local.lang,
			"sounds": hooks["sounds"],
			"boot": boot,
			"desk_theme": boot.get("desk_theme") or "Light",
			"csrf_token": csrf_token,
			"google_analytics_id": stylo.conf.get("google_analytics_id"),
			"google_analytics_anonymize_ip": stylo.conf.get("google_analytics_anonymize_ip"),
			"app_name": (
				stylo.get_website_settings("app_name") or stylo.get_system_settings("app_name") or "Stylo"
			),
		}
	)

	return context
