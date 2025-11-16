# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class UnhandledEmail(Document):
	pass


def remove_old_unhandled_emails():
	stylo.db.delete(
		"Unhandled Email", {"modified": ("<", stylo.utils.add_days(stylo.utils.nowdate(), -14))}
	)
