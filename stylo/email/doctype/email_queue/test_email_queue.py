# Copyright (c) 2015, Stylo Technologies and Contributors
# License: MIT. See LICENSE

import stylo
from stylo.tests.utils import StyloTestCase


class TestEmailQueue(StyloTestCase):
	def test_email_queue_deletion_based_on_modified_date(self):
		from stylo.email.doctype.email_queue.email_queue import EmailQueue

		old_record = stylo.get_doc(
			{
				"doctype": "Email Queue",
				"sender": "Test <test@example.com>",
				"show_as_cc": "",
				"message": "Test message",
				"status": "Sent",
				"priority": 1,
				"recipients": [
					{
						"recipient": "test_auth@test.com",
					}
				],
			}
		).insert()

		old_record.modified = "2010-01-01 00:00:01"
		old_record.recipients[0].modified = old_record.modified
		old_record.db_update_all()

		new_record = stylo.copy_doc(old_record)
		new_record.insert()

		EmailQueue.clear_old_logs()

		self.assertFalse(stylo.db.exists("Email Queue", old_record.name))
		self.assertFalse(stylo.db.exists("Email Queue Recipient", {"parent": old_record.name}))

		self.assertTrue(stylo.db.exists("Email Queue", new_record.name))
		self.assertTrue(stylo.db.exists("Email Queue Recipient", {"parent": new_record.name}))
