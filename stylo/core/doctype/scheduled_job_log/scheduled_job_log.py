# Copyright (c) 2019, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document
from stylo.query_builder import Interval
from stylo.query_builder.functions import Now


class ScheduledJobLog(Document):
	@staticmethod
	def clear_old_logs(days=90):
		table = stylo.qb.DocType("Scheduled Job Log")
		stylo.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
