import re

import stylo
from stylo.core.doctype.user.user import create_contact


def execute():
	"""Create Contact for each User if not present"""
	stylo.reload_doc("integrations", "doctype", "google_contacts")
	stylo.reload_doc("contacts", "doctype", "contact")
	stylo.reload_doc("core", "doctype", "dynamic_link")

	contact_meta = stylo.get_meta("Contact")
	if contact_meta.has_field("phone_nos") and contact_meta.has_field("email_ids"):
		stylo.reload_doc("contacts", "doctype", "contact_phone")
		stylo.reload_doc("contacts", "doctype", "contact_email")

	users = stylo.get_all("User", filters={"name": ("not in", "Administrator, Guest")}, fields=["*"])
	for user in users:
		if stylo.db.exists("Contact", {"email_id": user.email}) or stylo.db.exists(
			"Contact Email", {"email_id": user.email}
		):
			continue
		if user.first_name:
			user.first_name = re.sub("[<>]+", "", stylo.safe_decode(user.first_name))
		if user.last_name:
			user.last_name = re.sub("[<>]+", "", stylo.safe_decode(user.last_name))
		create_contact(user, ignore_links=True, ignore_mandatory=True)
