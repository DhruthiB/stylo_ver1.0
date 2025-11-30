# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors

from unittest.mock import patch

import stylo
from stylo.tests.utils import StyloTestCase


class TestClient(StyloTestCase):
	def test_set_value(self):
		todo = stylo.get_doc(dict(doctype="ToDo", description="test")).insert()
		stylo.set_value("ToDo", todo.name, "description", "test 1")
		self.assertEqual(stylo.get_value("ToDo", todo.name, "description"), "test 1")

		stylo.set_value("ToDo", todo.name, {"description": "test 2"})
		self.assertEqual(stylo.get_value("ToDo", todo.name, "description"), "test 2")

	def test_delete(self):
		from stylo.client import delete
		from stylo.desk.doctype.note.note import Note

		note = stylo.get_doc(
			doctype="Note",
			title=stylo.generate_hash(length=8),
			content="test",
			seen_by=[{"user": "Administrator"}],
		).insert()

		child_row_name = note.seen_by[0].name

		with patch.object(Note, "save") as save:
			delete("Note Seen By", child_row_name)
			save.assert_called()

		delete("Note", note.name)

		self.assertFalse(stylo.db.exists("Note", note.name))
		self.assertRaises(stylo.DoesNotExistError, delete, "Note", note.name)
		self.assertRaises(stylo.DoesNotExistError, delete, "Note Seen By", child_row_name)

	def test_http_valid_method_access(self):
		from stylo.client import delete
		from stylo.handler import execute_cmd

		stylo.set_user("Administrator")

		stylo.local.request = stylo._dict()
		stylo.local.request.method = "POST"

		stylo.local.form_dict = stylo._dict(
			{"doc": dict(doctype="ToDo", description="Valid http method"), "cmd": "stylo.client.save"}
		)
		todo = execute_cmd("stylo.client.save")

		self.assertEqual(todo.get("description"), "Valid http method")

		delete("ToDo", todo.name)

	def test_http_invalid_method_access(self):
		from stylo.handler import execute_cmd

		stylo.set_user("Administrator")

		stylo.local.request = stylo._dict()
		stylo.local.request.method = "GET"

		stylo.local.form_dict = stylo._dict(
			{"doc": dict(doctype="ToDo", description="Invalid http method"), "cmd": "stylo.client.save"}
		)

		self.assertRaises(stylo.PermissionError, execute_cmd, "stylo.client.save")

	def test_run_doc_method(self):
		from stylo.handler import execute_cmd

		if not stylo.db.exists("Report", "Test Run Doc Method"):
			report = stylo.get_doc(
				{
					"doctype": "Report",
					"ref_doctype": "User",
					"report_name": "Test Run Doc Method",
					"report_type": "Query Report",
					"is_standard": "No",
					"roles": [{"role": "System Manager"}],
				}
			).insert()
		else:
			report = stylo.get_doc("Report", "Test Run Doc Method")

		stylo.local.request = stylo._dict()
		stylo.local.request.method = "GET"

		# Whitelisted, works as expected
		stylo.local.form_dict = stylo._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "toggle_disable",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		execute_cmd(stylo.local.form_dict.cmd)

		# Not whitelisted, throws permission error
		stylo.local.form_dict = stylo._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "create_report_py",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		self.assertRaises(stylo.PermissionError, execute_cmd, stylo.local.form_dict.cmd)

	def test_array_values_in_request_args(self):
		import requests

		from stylo.auth import CookieManager, LoginManager

		stylo.utils.set_request(path="/")
		stylo.local.cookie_manager = CookieManager()
		stylo.local.login_manager = LoginManager()
		stylo.local.login_manager.login_as("Administrator")
		params = {
			"doctype": "DocType",
			"fields": ["name", "modified"],
			"sid": stylo.session.sid,
		}
		headers = {
			"accept": "application/json",
			"content-type": "application/json",
		}
		url = f"http://{stylo.local.site}:{stylo.conf.webserver_port}/api/method/stylo.client.get_list"
		res = requests.post(url, json=params, headers=headers)
		self.assertEqual(res.status_code, 200)
		data = res.json()
		first_item = data["message"][0]
		self.assertTrue("name" in first_item)
		self.assertTrue("modified" in first_item)
		stylo.local.login_manager.logout()

	def test_client_get(self):
		from stylo.client import get

		todo = stylo.get_doc(doctype="ToDo", description="test").insert()
		filters = {"name": todo.name}
		filters_json = stylo.as_json(filters)

		self.assertEqual(get("ToDo", filters=filters).description, "test")
		self.assertEqual(get("ToDo", filters=filters_json).description, "test")
		self.assertEqual(get("System Settings", "", "").doctype, "System Settings")
		self.assertEqual(get("ToDo", filters={}), get("ToDo", filters="{}"))
		todo.delete()

	def test_client_insert(self):
		from stylo.client import insert

		def get_random_title():
			return f"test-{stylo.generate_hash()}"

		# test insert dict
		doc = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(doc)
		self.assertTrue(note1)

		# test insert json
		doc["title"] = get_random_title()
		json_doc = stylo.as_json(doc)
		note2 = insert(json_doc)
		self.assertTrue(note2)

		# test insert child doc without parent fields
		child_doc = {"doctype": "Note Seen By", "user": "Administrator"}
		with self.assertRaises(stylo.ValidationError):
			insert(child_doc)

		# test insert child doc with parent fields
		child_doc = {
			"doctype": "Note Seen By",
			"user": "Administrator",
			"parenttype": "Note",
			"parent": note1.name,
			"parentfield": "seen_by",
		}
		note3 = insert(child_doc)
		self.assertTrue(note3)

		# cleanup
		stylo.delete_doc("Note", note1.name)
		stylo.delete_doc("Note", note2.name)

	def test_client_insert_many(self):
		from stylo.client import insert, insert_many

		def get_random_title():
			return f"test-{stylo.generate_hash(length=5)}"

		# insert a (parent) doc
		note1 = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(note1)

		doc_list = [
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{"doctype": "Note", "title": "not-a-random-title", "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": "another-note-title", "content": "test"},
		]

		# insert all docs
		docs = insert_many(doc_list)

		self.assertEqual(len(docs), 7)
		self.assertEqual(docs[3], "not-a-random-title")
		self.assertEqual(docs[6], "another-note-title")
		self.assertIn(note1.name, docs)

		# cleanup
		for doc in docs:
			stylo.delete_doc("Note", doc)
