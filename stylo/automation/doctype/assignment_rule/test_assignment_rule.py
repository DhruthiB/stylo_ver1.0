# Copyright (c) 2021, Stylo Technologies and Contributors
# License: MIT. See LICENSE

import stylo
from stylo.test_runner import make_test_records
from stylo.tests.utils import StyloTestCase
from stylo.utils import random_string


class TestAutoAssign(StyloTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		stylo.db.delete("Assignment Rule")

	@classmethod
	def tearDownClass(cls):
		stylo.db.rollback()

	def setUp(self):
		make_test_records("User")
		days = [
			dict(day="Sunday"),
			dict(day="Monday"),
			dict(day="Tuesday"),
			dict(day="Wednesday"),
			dict(day="Thursday"),
			dict(day="Friday"),
			dict(day="Saturday"),
		]
		self.days = days
		self.assignment_rule = get_assignment_rule([days, days])
		clear_assignments()

	def test_round_robin(self):
		note = make_note(dict(public=1))

		# check if auto assigned to first user
		self.assertEqual(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "allocated_to"
			),
			"test@example.com",
		)

		note = make_note(dict(public=1))

		# check if auto assigned to second user
		self.assertEqual(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "allocated_to"
			),
			"test1@example.com",
		)

		clear_assignments()

		note = make_note(dict(public=1))

		# check if auto assigned to third user, even if
		# previous assignments where closed
		self.assertEqual(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "allocated_to"
			),
			"test2@example.com",
		)

		# check loop back to first user
		note = make_note(dict(public=1))

		self.assertEqual(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "allocated_to"
			),
			"test@example.com",
		)

	def test_load_balancing(self):
		self.assignment_rule.rule = "Load Balancing"
		self.assignment_rule.save()

		for _ in range(30):
			make_note(dict(public=1))

		# check if each user has 10 assignments (?)
		for user in ("test@example.com", "test1@example.com", "test2@example.com"):
			self.assertEqual(len(stylo.get_all("ToDo", dict(allocated_to=user, reference_type="Note"))), 10)

		# clear 5 assignments for first user
		# can't do a limit in "delete" since postgres does not support it
		for d in stylo.get_all(
			"ToDo", dict(reference_type="Note", allocated_to="test@example.com"), limit=5
		):
			stylo.db.delete("ToDo", {"name": d.name})

		# add 5 more assignments
		for _i in range(5):
			make_note(dict(public=1))

		# check if each user still has 10 assignments
		for user in ("test@example.com", "test1@example.com", "test2@example.com"):
			self.assertEqual(len(stylo.get_all("ToDo", dict(allocated_to=user, reference_type="Note"))), 10)

	def test_assingment_on_guest_submissions(self):
		"""Sometimes documents are inserted as guest, check if assignment rules run on them. Use case: Web Forms"""
		with self.set_user("Guest"):
			doc = make_note({"public": 1}, ignore_permissions=True)

		# check assignment to *anyone*
		self.assertTrue(
			stylo.db.get_value(
				"ToDo",
				{"reference_type": "Note", "reference_name": doc.name, "status": "Open"},
				"allocated_to",
			),
		)

	def test_based_on_field(self):
		self.assignment_rule.rule = "Based on Field"
		self.assignment_rule.field = "owner"
		self.assignment_rule.save()

		stylo.set_user("test1@example.com")
		note = make_note(dict(public=1))
		# check if auto assigned to doc owner, test1@example.com
		self.assertEqual(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "owner"
			),
			"test1@example.com",
		)

		stylo.set_user("test2@example.com")
		note = make_note(dict(public=1))
		# check if auto assigned to doc owner, test2@example.com
		self.assertEqual(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "owner"
			),
			"test2@example.com",
		)

		stylo.set_user("Administrator")

	def test_assign_condition(self):
		# check condition
		note = make_note(dict(public=0))

		self.assertEqual(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "allocated_to"
			),
			None,
		)

	def test_clear_assignment(self):
		note = make_note(dict(public=1))

		# check if auto assigned to first user
		todo = stylo.get_list(
			"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), limit=1
		)[0]

		todo = stylo.get_doc("ToDo", todo["name"])
		self.assertEqual(todo.allocated_to, "test@example.com")

		# test auto unassign
		note.public = 0
		note.save()

		todo.load_from_db()

		# check if todo is cancelled
		self.assertEqual(todo.status, "Cancelled")

	def test_close_assignment(self):
		note = make_note(dict(public=1, content="valid"))

		# check if auto assigned
		todo = stylo.get_list(
			"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), limit=1
		)[0]

		todo = stylo.get_doc("ToDo", todo["name"])
		self.assertEqual(todo.allocated_to, "test@example.com")

		note.content = "Closed"
		note.save()

		todo.load_from_db()

		# check if todo is closed
		self.assertEqual(todo.status, "Closed")
		# check if closed todo retained assignment
		self.assertEqual(todo.allocated_to, "test@example.com")

	def check_multiple_rules(self):
		note = make_note(dict(public=1, notify_on_login=1))

		# check if auto assigned to test3 (2nd rule is applied, as it has higher priority)
		self.assertEqual(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "allocated_to"
			),
			"test@example.com",
		)

	def check_assignment_rule_scheduling(self):
		stylo.db.delete("Assignment Rule")

		days_1 = [dict(day="Sunday"), dict(day="Monday"), dict(day="Tuesday")]

		days_2 = [dict(day="Wednesday"), dict(day="Thursday"), dict(day="Friday"), dict(day="Saturday")]

		get_assignment_rule([days_1, days_2], ["public == 1", "public == 1"])

		stylo.flags.assignment_day = "Monday"
		note = make_note(dict(public=1))

		self.assertIn(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "allocated_to"
			),
			["test@example.com", "test1@example.com", "test2@example.com"],
		)

		stylo.flags.assignment_day = "Friday"
		note = make_note(dict(public=1))

		self.assertIn(
			stylo.db.get_value(
				"ToDo", dict(reference_type="Note", reference_name=note.name, status="Open"), "allocated_to"
			),
			["test3@example.com"],
		)

	def test_assignment_rule_condition(self):
		stylo.db.delete("Assignment Rule")

		# Add expiry_date custom field
		from stylo.custom.doctype.custom_field.custom_field import create_custom_field

		df = dict(fieldname="expiry_date", label="Expiry Date", fieldtype="Date")
		create_custom_field("Note", df)

		assignment_rule = stylo.get_doc(
			dict(
				name="Assignment with Due Date",
				doctype="Assignment Rule",
				document_type="Note",
				assign_condition="public == 0",
				due_date_based_on="expiry_date",
				assignment_days=self.days,
				users=[
					dict(user="test@example.com"),
				],
			)
		).insert()

		expiry_date = stylo.utils.add_days(stylo.utils.nowdate(), 2)
		note1 = make_note({"expiry_date": expiry_date})
		note2 = make_note({"expiry_date": expiry_date})

		note1_todo = stylo.get_all(
			"ToDo", filters=dict(reference_type="Note", reference_name=note1.name, status="Open")
		)[0]

		note1_todo_doc = stylo.get_doc("ToDo", note1_todo.name)
		self.assertEqual(stylo.utils.get_date_str(note1_todo_doc.date), expiry_date)

		# due date should be updated if the reference doc's date is updated.
		note1.expiry_date = stylo.utils.add_days(expiry_date, 2)
		note1.save()
		note1_todo_doc.reload()
		self.assertEqual(stylo.utils.get_date_str(note1_todo_doc.date), note1.expiry_date)

		# saving one note's expiry should not update other note todo's due date
		note2_todo = stylo.get_all(
			"ToDo",
			filters=dict(reference_type="Note", reference_name=note2.name, status="Open"),
			fields=["name", "date"],
		)[0]
		self.assertNotEqual(stylo.utils.get_date_str(note2_todo.date), note1.expiry_date)
		self.assertEqual(stylo.utils.get_date_str(note2_todo.date), expiry_date)
		assignment_rule.delete()
		stylo.db.commit()  # undo changes commited by DDL

	def test_submittable_assignment(self):
		# create a submittable doctype
		submittable_doctype = "Assignment Test Submittable"
		create_test_doctype(submittable_doctype)
		dt = stylo.get_doc("DocType", submittable_doctype)
		dt.is_submittable = 1
		dt.save()

		# create a rule for the submittable doctype
		assignment_rule = stylo.new_doc("Assignment Rule")
		assignment_rule.name = f"For {submittable_doctype}"
		assignment_rule.document_type = submittable_doctype
		assignment_rule.rule = "Round Robin"
		assignment_rule.extend("assignment_days", self.days)
		assignment_rule.append("users", {"user": "test@example.com"})
		assignment_rule.assign_condition = "docstatus == 1"
		assignment_rule.unassign_condition = "docstatus == 2"
		assignment_rule.save()

		# create a submittable doc
		doc = stylo.new_doc(submittable_doctype)
		doc.save()
		doc.submit()

		# check if todo is created
		todos = stylo.get_all(
			"ToDo",
			filters={
				"reference_type": submittable_doctype,
				"reference_name": doc.name,
				"status": "Open",
				"allocated_to": "test@example.com",
			},
		)
		self.assertEqual(len(todos), 1)

		# check if todo is closed on cancel
		doc.cancel()
		todos = stylo.get_all(
			"ToDo",
			filters={
				"reference_type": submittable_doctype,
				"reference_name": doc.name,
				"status": "Cancelled",
				"allocated_to": "test@example.com",
			},
		)
		self.assertEqual(len(todos), 1)


def clear_assignments():
	stylo.db.delete("ToDo", {"reference_type": "Note"})


def get_assignment_rule(days, assign=None):
	stylo.delete_doc_if_exists("Assignment Rule", "For Note 1")

	if not assign:
		assign = ["public == 1", "notify_on_login == 1"]

	assignment_rule = stylo.get_doc(
		dict(
			name="For Note 1",
			doctype="Assignment Rule",
			priority=0,
			document_type="Note",
			assign_condition=assign[0],
			unassign_condition="public == 0 or notify_on_login == 1",
			close_condition='"Closed" in content',
			rule="Round Robin",
			assignment_days=days[0],
			users=[
				dict(user="test@example.com"),
				dict(user="test1@example.com"),
				dict(user="test2@example.com"),
			],
		)
	).insert()

	stylo.delete_doc_if_exists("Assignment Rule", "For Note 2")

	# 2nd rule
	stylo.get_doc(
		dict(
			name="For Note 2",
			doctype="Assignment Rule",
			priority=1,
			document_type="Note",
			assign_condition=assign[1],
			unassign_condition="notify_on_login == 0",
			rule="Round Robin",
			assignment_days=days[1],
			users=[dict(user="test3@example.com")],
		)
	).insert()

	return assignment_rule


def make_note(values=None, *, ignore_permissions=False):
	note = stylo.get_doc(dict(doctype="Note", title=random_string(10), content=random_string(20)))

	if values:
		note.update(values)

	note.insert(ignore_permissions=ignore_permissions)

	return note


def create_test_doctype(doctype: str):
	"""Create custom doctype."""
	stylo.delete_doc("DocType", doctype)

	stylo.get_doc(
		{
			"doctype": "DocType",
			"name": doctype,
			"module": "Custom",
			"custom": 1,
			"fields": [
				{
					"fieldname": "expiry_date",
					"label": "Expiry Date",
					"fieldtype": "Date",
				},
				{
					"fieldname": "notify_on_login",
					"label": "Notify on Login",
					"fieldtype": "Check",
				},
				{
					"fieldname": "public",
					"label": "Public",
					"fieldtype": "Check",
				},
				{
					"fieldname": "content",
					"label": "Content",
					"fieldtype": "Text",
				},
			],
			"permissions": [
				{
					"create": 1,
					"delete": 1,
					"email": 1,
					"export": 1,
					"print": 1,
					"read": 1,
					"report": 1,
					"role": "All",
					"share": 1,
					"write": 1,
				},
			],
		}
	).insert()
