# Copyright (c) 2018, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	signatures = stylo.db.get_list("User", {"email_signature": ["!=", ""]}, ["name", "email_signature"])
	stylo.reload_doc("core", "doctype", "user")
	for d in signatures:
		signature = d.get("email_signature")
		signature = signature.replace("\n", "<br>")
		signature = "<div>" + signature + "</div>"
		stylo.db.set_value("User", d.get("name"), "email_signature", signature)
