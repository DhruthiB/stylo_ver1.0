# Copyright (c) 2018, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class ViewLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		viewed_by: DF.Data | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=180):
		from stylo.query_builder import Interval
		from stylo.query_builder.functions import Now

		table = stylo.qb.DocType("View Log")
		stylo.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))
