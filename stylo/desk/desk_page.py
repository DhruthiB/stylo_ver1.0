# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def get(name):
	"""
	Return the :term:`doclist` of the `Page` specified by `name`
	"""
	page = stylo.get_doc("Page", name)
	if page.is_permitted():
		page.load_assets()
		docs = stylo._dict(page.as_dict())
		if getattr(page, "_dynamic_page", None):
			docs["_dynamic_page"] = 1

		return docs
	else:
		stylo.response["403"] = 1
		raise stylo.PermissionError("No read permission for Page %s" % (page.title or name))


@stylo.whitelist(allow_guest=True)
def getpage(name: str):
	"""
	Load the page from `stylo.form` and send it via `stylo.response`
	"""

	doc = get(name)
	stylo.response.docs.append(doc)


def has_permission(page):
	if stylo.session.user == "Administrator" or "System Manager" in stylo.get_roles():
		return True

	page_roles = [d.role for d in page.get("roles")]
	if page_roles:
		if stylo.session.user == "Guest" and "Guest" not in page_roles:
			return False
		elif not set(page_roles).intersection(set(stylo.get_roles())):
			# check if roles match
			return False

	if not stylo.has_permission("Page", ptype="read", doc=page):
		# check if there are any user_permissions
		return False
	else:
		# hack for home pages! if no Has Roles, allow everyone to see!
		return True
