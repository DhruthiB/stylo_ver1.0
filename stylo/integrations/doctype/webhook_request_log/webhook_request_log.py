# Copyright (c) 2021, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class WebhookRequestLog(Document):
	@staticmethod
	def clear_old_logs(days=30):
		from stylo.query_builder import Interval
		from stylo.query_builder.functions import Now

		table = stylo.qb.DocType("Webhook Request Log")
		stylo.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
