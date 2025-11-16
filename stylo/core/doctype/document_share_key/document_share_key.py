# Copyright (c) 2021, Stylo Technologies and contributors
# For license information, please see license.txt

from random import randrange

import stylo
from stylo.model.document import Document


class DocumentShareKey(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		expires_on: DF.Date | None
		key: DF.Data | None
		reference_docname: DF.DynamicLink | None
		reference_doctype: DF.Link | None
	# end: auto-generated types

	def before_insert(self):
		self.key = stylo.generate_hash(length=randrange(25, 35))
		if not self.expires_on and not self.flags.no_expiry:
			self.expires_on = stylo.utils.add_days(
				None, days=stylo.get_system_settings("document_share_key_expiry") or 90
			)


def is_expired(expires_on):
	return expires_on and expires_on < stylo.utils.getdate()
