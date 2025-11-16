# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class UnhandledEmail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		email_account: DF.Link | None
		message_id: DF.Code | None
		raw: DF.Code | None
		reason: DF.LongText | None
		uid: DF.Data | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		stylo.db.delete(
			"Unhandled Email",
			{
				"creation": ("<", stylo.utils.add_days(stylo.utils.nowdate(), -1 * days)),
			},
		)
