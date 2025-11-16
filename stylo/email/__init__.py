# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo
from stylo.desk.reportview import build_match_conditions


def sendmail_to_system_managers(subject, content):
	stylo.sendmail(recipients=get_system_managers(), subject=subject, content=content)


@stylo.whitelist()
def get_contact_list(txt, page_length=20) -> list[dict]:
	"""Return email ids for a multiselect field."""

	if cached_contacts := get_cached_contacts(txt):
		return cached_contacts[:page_length]

	reportview_conditions = build_match_conditions("Contact")
	match_conditions = f"and {reportview_conditions}" if reportview_conditions else ""

	# The multiselect field will store the `label` as the selected value.
	# The `value` is just used as a unique key to distinguish between the options.
	# https://github.com/stylo/stylo/blob/6c6a89bcdd9454060a1333e23b855d0505c9ebc2/stylo/public/js/stylo/form/controls/autocomplete.js#L29-L35
	out = stylo.db.sql(
		f"""select name as value, email_id as label,
		concat(first_name, ifnull(concat(' ',last_name), '' )) as description
		from tabContact
		where (name like %(txt)s or email_id like %(txt)s) and email_id != ''
		{match_conditions}
		limit %(page_length)s""",
		{"txt": f"%{txt}%", "page_length": page_length},
		as_dict=True,
	)
	out = list(filter(None, out))

	update_contact_cache(out)

	return out


def get_system_managers():
	return stylo.db.sql_list(
		"""select parent FROM `tabHas Role`
		WHERE role='System Manager'
		AND parent!='Administrator'
		AND parent IN (SELECT email FROM tabUser WHERE enabled=1)"""
	)


@stylo.whitelist()
def relink(name, reference_doctype=None, reference_name=None):
	stylo.db.sql(
		"""update
			`tabCommunication`
		set
			reference_doctype = %s,
			reference_name = %s,
			status = "Linked"
		where
			communication_type = "Communication" and
			name = %s""",
		(reference_doctype, reference_name, name),
	)


@stylo.whitelist()
@stylo.validate_and_sanitize_search_inputs
def get_communication_doctype(doctype, txt, searchfield, start, page_len, filters):
	user_perms = stylo.utils.user.UserPermissions(stylo.session.user)
	user_perms.build_permissions()
	can_read = user_perms.can_read
	from stylo.modules import load_doctype_module

	com_doctypes = []
	if len(txt) < 2:
		for name in stylo.get_hooks("communication_doctypes"):
			try:
				module = load_doctype_module(name, suffix="_dashboard")
				if hasattr(module, "get_data"):
					for i in module.get_data()["transactions"]:
						com_doctypes += i["items"]
			except ImportError:
				pass
	else:
		com_doctypes = [
			d[0] for d in stylo.db.get_values("DocType", {"issingle": 0, "istable": 0, "hide_toolbar": 0})
		]

	out = []
	for dt in list(set(com_doctypes)):
		if txt.lower().replace("%", "") in dt.lower() and dt in can_read:
			out.append([dt])
	return out


def get_cached_contacts(txt):
	contacts = stylo.cache().hget("contacts", stylo.session.user) or []

	if not contacts:
		return

	if not txt:
		return contacts

	match = [
		d
		for d in contacts
		if (d.value and ((d.value and txt in d.value) or (d.description and txt in d.description)))
	]
	return match


def update_contact_cache(contacts):
	cached_contacts = stylo.cache().hget("contacts", stylo.session.user) or []

	uncached_contacts = [d for d in contacts if d not in cached_contacts]
	cached_contacts.extend(uncached_contacts)

	stylo.cache().hset("contacts", stylo.session.user, cached_contacts)
