# Copyright (c) 2019, Stylo Technologies and Contributors
# License: MIT. See LICENSE
import json

import stylo
from stylo.contacts.doctype.contact.contact import get_contact_name
from stylo.core.doctype.user.user import create_contact
from stylo.tests.utils import StyloTestCase
from stylo.website.doctype.personal_data_download_request.personal_data_download_request import (
	get_user_data,
)


class TestRequestPersonalData(StyloTestCase):
	def setUp(self):
		create_user_if_not_exists(email="test_privacy@example.com")

	def tearDown(self):
		stylo.db.delete("Personal Data Download Request")

	def test_user_data_creation(self):
		user_data = json.loads(get_user_data("test_privacy@example.com"))
		contact_name = get_contact_name("test_privacy@example.com")
		expected_data = {"Contact": stylo.get_all("Contact", {"name": contact_name}, ["*"])}
		expected_data = json.loads(json.dumps(expected_data, default=str))
		self.assertEqual({"Contact": user_data["Contact"]}, expected_data)

	def test_file_and_email_creation(self):
		stylo.set_user("test_privacy@example.com")
		download_request = stylo.get_doc(
			{"doctype": "Personal Data Download Request", "user": "test_privacy@example.com"}
		)
		download_request.save(ignore_permissions=True)

		stylo.set_user("Administrator")

		file_count = stylo.db.count(
			"File",
			{
				"attached_to_doctype": "Personal Data Download Request",
				"attached_to_name": download_request.name,
			},
		)

		self.assertEqual(file_count, 1)

		email_queue = stylo.get_all("Email Queue", fields=["message"], order_by="creation DESC", limit=1)
		self.assertIn(stylo._("Download Your Data"), email_queue[0].message)

		stylo.db.delete("Email Queue")


def create_user_if_not_exists(email, first_name=None):
	stylo.delete_doc_if_exists("User", email)

	user = stylo.get_doc(
		{
			"doctype": "User",
			"user_type": "Website User",
			"email": email,
			"send_welcome_email": 0,
			"first_name": first_name or email.split("@", 1)[0],
			"birth_date": stylo.utils.now_datetime(),
		}
	).insert(ignore_permissions=True)
	create_contact(user=user)
