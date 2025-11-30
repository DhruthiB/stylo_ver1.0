# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo import _
from stylo.model.document import Document
from stylo.utils import cint


class BulkUpdate(Document):
	@stylo.whitelist()
	def bulk_update(self):
		self.check_permission("write")
		limit = self.limit if self.limit and cint(self.limit) < 500 else 500

		condition = ""
		if self.condition:
			if ";" in self.condition:
				stylo.throw(_("; not allowed in condition"))

			condition = f" where {self.condition}"

		docnames = stylo.db.sql_list(
			f"""select name from `tab{self.document_type}`{condition} limit {limit} offset 0"""
		)
		return submit_cancel_or_update_docs(
			self.document_type, docnames, "update", {self.field: self.update_value}
		)


@stylo.whitelist()
def submit_cancel_or_update_docs(doctype, docnames, action="submit", data=None):
	if isinstance(docnames, str):
		docnames = stylo.parse_json(docnames)

	if len(docnames) < 20:
		return _bulk_action(doctype, docnames, action, data)
	elif len(docnames) <= 500:
		stylo.msgprint(_("Bulk operation is enqueued in background."), alert=True)
		stylo.enqueue(
			_bulk_action,
			doctype=doctype,
			docnames=docnames,
			action=action,
			data=data,
			queue="short",
			timeout=1000,
		)
	else:
		stylo.throw(_("Bulk operations only support up to 500 documents."), title=_("Too Many Documents"))


def _bulk_action(doctype, docnames, action, data):
	if data:
		data = stylo.parse_json(data)

	failed = []

	for i, d in enumerate(docnames, 1):
		doc = stylo.get_doc(doctype, d)
		try:
			message = ""
			if action == "submit" and doc.docstatus.is_draft():
				doc.submit()
				message = _("Submitting {0}").format(doctype)
			elif action == "cancel" and doc.docstatus.is_submitted():
				doc.cancel()
				message = _("Cancelling {0}").format(doctype)
			elif action == "update" and not doc.docstatus.is_cancelled():
				doc.update(data)
				doc.save()
				message = _("Updating {0}").format(doctype)
			else:
				failed.append(d)
			stylo.db.commit()
			show_progress(docnames, message, i, d)

		except Exception:
			failed.append(d)
			stylo.db.rollback()

	return failed


def show_progress(docnames, message, i, description):
	n = len(docnames)
	stylo.publish_progress(float(i) * 100 / n, title=message, description=description)
