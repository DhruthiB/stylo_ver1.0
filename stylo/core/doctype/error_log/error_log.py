# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document
from stylo.query_builder import Interval
from stylo.query_builder.functions import Now


class ErrorLog(Document):
	def onload(self):
		if not self.seen and not stylo.flags.read_only:
			self.db_set("seen", 1, update_modified=0)
			stylo.db.commit()

	@staticmethod
	def clear_old_logs(days=30):
		table = stylo.qb.DocType("Error Log")
		stylo.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@stylo.whitelist()
def clear_error_logs():
	"""Flush all Error Logs"""
	stylo.only_for("System Manager")
	stylo.db.truncate("Error Log")
