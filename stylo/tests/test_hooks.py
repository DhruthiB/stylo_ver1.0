# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.cache_manager import clear_controller_cache
from stylo.desk.doctype.todo.todo import ToDo
from stylo.tests.test_api import StyloAPITestCase
from stylo.tests.utils import StyloTestCase, patch_hooks


class TestHooks(StyloTestCase):
	def test_hooks(self):
		hooks = stylo.get_hooks()
		self.assertTrue(isinstance(hooks.get("app_name"), list))
		self.assertTrue(isinstance(hooks.get("doc_events"), dict))
		self.assertTrue(isinstance(hooks.get("doc_events").get("*"), dict))
		self.assertTrue(isinstance(hooks.get("doc_events").get("*"), dict))
		self.assertTrue(
			"stylo.desk.notifications.clear_doctype_notifications"
			in hooks.get("doc_events").get("*").get("on_update")
		)

	def test_override_doctype_class(self):
		from stylo import hooks

		# Set hook
		hooks.override_doctype_class = {"ToDo": ["stylo.tests.test_hooks.CustomToDo"]}

		# Clear cache
		stylo.cache().delete_value("app_hooks")
		clear_controller_cache("ToDo")

		todo = stylo.get_doc(doctype="ToDo", description="asdf")
		self.assertTrue(isinstance(todo, CustomToDo))

	def test_has_permission(self):
		from stylo import hooks

		# Set hook
		address_has_permission_hook = hooks.has_permission.get("Address", [])
		if isinstance(address_has_permission_hook, str):
			address_has_permission_hook = [address_has_permission_hook]

		address_has_permission_hook.append("stylo.tests.test_hooks.custom_has_permission")

		hooks.has_permission["Address"] = address_has_permission_hook

		wildcard_has_permission_hook = hooks.has_permission.get("*", [])
		if isinstance(wildcard_has_permission_hook, str):
			wildcard_has_permission_hook = [wildcard_has_permission_hook]

		wildcard_has_permission_hook.append("stylo.tests.test_hooks.custom_has_permission")

		hooks.has_permission["*"] = wildcard_has_permission_hook

		# Clear cache
		stylo.cache().delete_value("app_hooks")

		# Init User and Address
		username = "test@example.com"
		user = stylo.get_doc("User", username)
		user.add_roles("System Manager")
		address = stylo.new_doc("Address")

		# Create Note
		note = stylo.new_doc("Note")
		note.public = 1

		# Test!
		self.assertTrue(stylo.has_permission("Address", doc=address, user=username))
		self.assertTrue(stylo.has_permission("Note", doc=note, user=username))

		address.flags.dont_touch_me = True
		self.assertFalse(stylo.has_permission("Address", doc=address, user=username))

		note.flags.dont_touch_me = True
		self.assertFalse(stylo.has_permission("Note", doc=note, user=username))

	def test_ignore_links_on_delete(self):
		email_unsubscribe = stylo.get_doc(
			{"doctype": "Email Unsubscribe", "email": "test@example.com", "global_unsubscribe": 1}
		).insert()

		event = stylo.get_doc(
			{
				"doctype": "Event",
				"subject": "Test Event",
				"starts_on": "2022-12-21",
				"event_type": "Public",
				"event_participants": [
					{
						"reference_doctype": "Email Unsubscribe",
						"reference_docname": email_unsubscribe.name,
					}
				],
			}
		).insert()
		self.assertRaises(stylo.LinkExistsError, email_unsubscribe.delete)

		event.event_participants = []
		event.save()

		todo = stylo.get_doc(
			{
				"doctype": "ToDo",
				"description": "Test ToDo",
				"reference_type": "Event",
				"reference_name": event.name,
			}
		)
		todo.insert()

		event.delete()


class TestAPIHooks(StyloAPITestCase):
	def test_auth_hook(self):
		with patch_hooks({"auth_hooks": ["stylo.tests.test_hooks.custom_auth"]}):
			site_url = stylo.utils.get_site_url(stylo.local.site)
			response = self.get(
				site_url + "/api/method/stylo.auth.get_logged_user",
				headers={"Authorization": "Bearer set_test_example_user"},
			)
			# Test!
			self.assertTrue(response.json.get("message") == "test@example.com")


def custom_has_permission(doc, ptype, user):
	if doc.flags.dont_touch_me:
		return False


def custom_auth():
	auth_type, token = stylo.get_request_header("Authorization", "Bearer ").split(" ")
	if token == "set_test_example_user":
		stylo.set_user("test@example.com")


class CustomToDo(ToDo):
	pass
