# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document
from stylo.query_builder import Interval
from stylo.query_builder.functions import Now
from stylo.utils.data import add_to_date


class OAuthBearerToken(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		access_token: DF.Data | None
		client: DF.Link | None
		expiration_time: DF.Datetime | None
		expires_in: DF.Int
		refresh_token: DF.Data | None
		scopes: DF.Text | None
		status: DF.Literal["Active", "Revoked"]
		user: DF.Link
	# end: auto-generated types

	def validate(self):
		if not self.expiration_time:
			self.expiration_time = add_to_date(self.creation, seconds=self.expires_in, as_datetime=True)

	@staticmethod
	def clear_old_logs(days=30):
		table = stylo.qb.DocType("OAuth Bearer Token")
		stylo.db.delete(
			table,
			filters=(table.expiration_time < (Now() - Interval(days=days))),
		)
