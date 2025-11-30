# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo
import stylo.permissions
from stylo import _
from stylo.core.doctype.activity_log.activity_log import add_authentication_log
from stylo.utils import get_fullname


def update_feed(doc, method=None):
	if stylo.flags.in_patch or stylo.flags.in_install or stylo.flags.in_import:
		return

	if doc._action != "save" or doc.flags.ignore_feed:
		return

	if doc.doctype == "Activity Log" or doc.meta.issingle:
		return

	if hasattr(doc, "get_feed"):
		feed = doc.get_feed()

		if feed:
			if isinstance(feed, str):
				feed = {"subject": feed}

			feed = stylo._dict(feed)
			doctype = feed.doctype or doc.doctype
			name = feed.name or doc.name

			# delete earlier feed
			stylo.db.delete(
				"Activity Log",
				{"reference_doctype": doctype, "reference_name": name, "link_doctype": feed.link_doctype},
			)

			stylo.get_doc(
				{
					"doctype": "Activity Log",
					"reference_doctype": doctype,
					"reference_name": name,
					"subject": feed.subject,
					"full_name": get_fullname(doc.owner),
					"reference_owner": stylo.db.get_value(doctype, name, "owner"),
					"link_doctype": feed.link_doctype,
					"link_name": feed.link_name,
				}
			).insert(ignore_permissions=True)


def login_feed(login_manager):
	if login_manager.user != "Guest":
		subject = _("{0} logged in").format(get_fullname(login_manager.user))
		add_authentication_log(subject, login_manager.user)


def logout_feed(user, reason):
	if user and user != "Guest":
		subject = _("{0} logged out: {1}").format(get_fullname(user), stylo.bold(reason))
		add_authentication_log(subject, user, operation="Logout")


def get_feed_match_conditions(user=None, doctype="Comment"):
	if not user:
		user = stylo.session.user

	conditions = [
		"`tab{doctype}`.owner={user} or `tab{doctype}`.reference_owner={user}".format(
			user=stylo.db.escape(user), doctype=doctype
		)
	]

	user_permissions = stylo.permissions.get_user_permissions(user)
	can_read = stylo.get_user().get_can_read()

	can_read_doctypes = [f"'{dt}'" for dt in list(set(can_read) - set(list(user_permissions)))]

	if can_read_doctypes:
		conditions += [
			"""(`tab{doctype}`.reference_doctype is null
			or `tab{doctype}`.reference_doctype = ''
			or `tab{doctype}`.reference_doctype
			in ({values}))""".format(doctype=doctype, values=", ".join(can_read_doctypes))
		]

		if user_permissions:
			can_read_docs = []
			for dt, obj in user_permissions.items():
				for n in obj:
					can_read_docs.append(
						"{}|{}".format(stylo.db.escape(dt), stylo.db.escape(n.get("doc", "")))
					)

			if can_read_docs:
				conditions.append(
					"concat_ws('|', `tab{doctype}`.reference_doctype, `tab{doctype}`.reference_name) in ({values})".format(
						doctype=doctype, values=", ".join(can_read_docs)
					)
				)

	return "(" + " or ".join(conditions) + ")"
