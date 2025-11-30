# Copyright (c) 2018, Stylo Technologies and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.tests.utils import StyloTestCase


class TestViewLog(StyloTestCase):
	def tearDown(self):
		stylo.set_user("Administrator")

	def test_if_user_is_added(self):
		ev = stylo.get_doc(
			{
				"doctype": "Event",
				"subject": "test event for view logs",
				"starts_on": "2018-06-04 14:11:00",
				"event_type": "Public",
			}
		).insert()

		stylo.set_user("test@example.com")

		from stylo.desk.form.load import getdoc

		# load the form
		getdoc("Event", ev.name)
		a = stylo.get_value(
			doctype="View Log",
			filters={"reference_doctype": "Event", "reference_name": ev.name},
			fieldname=["viewed_by"],
		)

		self.assertEqual("test@example.com", a)
		self.assertNotEqual("test1@example.com", a)
