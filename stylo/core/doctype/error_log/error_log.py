# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document
from stylo.query_builder import Interval
from stylo.query_builder.functions import Now


class ErrorLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		error: DF.Code | None
		method: DF.Data | None
		reference_doctype: DF.Link | None
		reference_name: DF.Data | None
		seen: DF.Check
		trace_id: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.method = str(self.method)
		self.error = str(self.error)

		if len(self.method) > 140:
			self.error = f"{self.method}\n{self.error}"
			self.method = self.method[:140]

	def onload(self):
		if not self.seen and not stylo.flags.read_only:
			self.db_set("seen", 1, update_modified=0)
			stylo.db.commit()

	@staticmethod
	def clear_old_logs(days=30):
		table = stylo.qb.DocType("Error Log")
		stylo.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@stylo.whitelist()
def clear_error_logs():
	"""Flush all Error Logs"""
	stylo.only_for("System Manager")
	stylo.db.truncate("Error Log")
