# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import json

import stylo
from stylo import _
from stylo.desk.doctype.bulk_update.bulk_update import show_progress
from stylo.model.document import Document
from stylo.model.workflow import get_workflow_name


class DeletedDocument(Document):
	no_feed_on_delete = True

	@staticmethod
	def clear_old_logs(days=180):
		from stylo.query_builder import Interval
		from stylo.query_builder.functions import Now

		table = stylo.qb.DocType("Deleted Document")
		stylo.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@stylo.whitelist()
def restore(name, alert=True):
	deleted = stylo.get_doc("Deleted Document", name)

	if deleted.restored:
		stylo.throw(_("Document {0} Already Restored").format(name), exc=stylo.DocumentAlreadyRestored)

	doc = stylo.get_doc(json.loads(deleted.data))

	try:
		doc.insert()
	except stylo.DocstatusTransitionError:
		stylo.msgprint(_("Cancelled Document restored as Draft"))
		doc.docstatus = 0
		active_workflow = get_workflow_name(doc.doctype)
		if active_workflow:
			workflow_state_fieldname = stylo.get_value("Workflow", active_workflow, "workflow_state_field")
			if doc.get(workflow_state_fieldname):
				doc.set(workflow_state_fieldname, None)
		doc.insert()

	doc.add_comment("Edit", _("restored {0} as {1}").format(deleted.deleted_name, doc.name))

	deleted.new_name = doc.name
	deleted.restored = 1
	deleted.db_update()

	if alert:
		stylo.msgprint(_("Document Restored"))


@stylo.whitelist()
def bulk_restore(docnames):
	docnames = stylo.parse_json(docnames)
	message = _("Restoring Deleted Document")
	restored, invalid, failed = [], [], []

	for i, d in enumerate(docnames):
		try:
			show_progress(docnames, message, i + 1, d)
			restore(d, alert=False)
			stylo.db.commit()
			restored.append(d)

		except stylo.DocumentAlreadyRestored:
			stylo.message_log.pop()
			invalid.append(d)

		except Exception:
			stylo.message_log.pop()
			failed.append(d)
			stylo.db.rollback()

	return {"restored": restored, "invalid": invalid, "failed": failed}
