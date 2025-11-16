# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo
import stylo.www.list
from stylo import _

no_cache = 1


def get_context(context):
	if stylo.session.user == "Guest":
		stylo.throw(_("You need to be logged in to access this page"), stylo.PermissionError)

	context.current_user = stylo.get_doc("User", stylo.session.user)
	context.show_sidebar = True
