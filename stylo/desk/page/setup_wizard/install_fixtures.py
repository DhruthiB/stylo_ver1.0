# Copyright (c) 2021, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo
from stylo.desk.doctype.global_search_settings.global_search_settings import (
	update_global_search_doctypes,
)
from stylo.utils.dashboard import sync_dashboards


def install():
	update_genders()
	update_salutations()
	update_global_search_doctypes()
	sync_dashboards()
	add_unsubscribe()


@stylo.whitelist()
def update_genders():
	default_genders = [
		"Male",
		"Female",
		"Other",
		"Transgender",
		"Genderqueer",
		"Non-Conforming",
		"Prefer not to say",
	]
	records = [{"doctype": "Gender", "gender": d} for d in default_genders]
	for record in records:
		stylo.get_doc(record).insert(ignore_permissions=True, ignore_if_duplicate=True)


@stylo.whitelist()
def update_salutations():
	default_salutations = ["Mr", "Ms", "Mx", "Dr", "Mrs", "Madam", "Miss", "Master", "Prof"]
	records = [{"doctype": "Salutation", "salutation": d} for d in default_salutations]
	for record in records:
		doc = stylo.new_doc(record.get("doctype"))
		doc.update(record)
		doc.insert(ignore_permissions=True, ignore_if_duplicate=True)


def add_unsubscribe():
	email_unsubscribe = [
		{"email": "admin@example.com", "global_unsubscribe": 1},
		{"email": "guest@example.com", "global_unsubscribe": 1},
	]

	for unsubscribe in email_unsubscribe:
		if not stylo.get_all("Email Unsubscribe", filters=unsubscribe):
			doc = stylo.new_doc("Email Unsubscribe")
			doc.update(unsubscribe)
			doc.insert(ignore_permissions=True)
