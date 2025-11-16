# Copyright (c) 2021, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class WebhookRequestLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		data: DF.Code | None
		error: DF.Text | None
		headers: DF.Code | None
		reference_doctype: DF.Data | None
		reference_document: DF.Data | None
		response: DF.Code | None
		url: DF.Text | None
		user: DF.Link | None
		webhook: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from stylo.query_builder import Interval
		from stylo.query_builder.functions import Now

		table = stylo.qb.DocType("Webhook Request Log")
		stylo.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))
