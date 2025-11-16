# Copyright (c) 2019, Stylo Technologies and contributors
# License: MIT. See LICENSE

import json

import stylo
from stylo import _
from stylo.model.document import Document


class SessionDefaultSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.core.doctype.session_default.session_default import SessionDefault
		from stylo.types import DF

		session_defaults: DF.Table[SessionDefault]
	# end: auto-generated types

	pass


@stylo.whitelist()
def get_session_default_values():
	settings = stylo.get_single("Session Default Settings")
	fields = []
	for default_values in settings.session_defaults:
		reference_doctype = stylo.scrub(default_values.ref_doctype)
		fields.append(
			{
				"fieldname": reference_doctype,
				"fieldtype": "Link",
				"options": default_values.ref_doctype,
				"label": _("Default {0}").format(_(default_values.ref_doctype)),
				"default": stylo.defaults.get_user_default(reference_doctype),
			}
		)
	return json.dumps(fields)


@stylo.whitelist()
def set_session_default_values(default_values):
	default_values = stylo.parse_json(default_values)
	for entry in default_values:
		try:
			stylo.defaults.set_user_default(entry, default_values.get(entry))
		except Exception:
			return
	return "success"


# called on hook 'on_logout' to clear defaults for the session
def clear_session_defaults():
	settings = stylo.get_single("Session Default Settings").session_defaults
	for entry in settings:
		stylo.defaults.clear_user_default(stylo.scrub(entry.ref_doctype))
