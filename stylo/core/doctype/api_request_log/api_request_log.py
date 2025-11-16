# Copyright (c) 2025, Stylo Technologies and contributors
# For license information, please see license.txt

import stylo
from stylo.model.document import Document


class APIRequestLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		method: DF.Data | None
		path: DF.Data | None
		user: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days: int = 90):
		from stylo.query_builder import Interval
		from stylo.query_builder.functions import Now

		table = stylo.qb.DocType("API Request Log")
		stylo.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))
