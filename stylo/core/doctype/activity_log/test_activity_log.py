# Copyright (c) 2015, Stylo Technologies and Contributors
# License: MIT. See LICENSE
import time

import stylo
from stylo.auth import CookieManager, LoginManager
from stylo.tests.utils import StyloTestCase


class TestActivityLog(StyloTestCase):
	def test_activity_log(self):
		# test user login log
		stylo.local.form_dict = stylo._dict(
			{
				"cmd": "login",
				"sid": "Guest",
				"pwd": stylo.conf.admin_password or "admin",
				"usr": "Administrator",
			}
		)

		stylo.local.request_ip = "127.0.0.1"
		stylo.local.cookie_manager = CookieManager()
		stylo.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertFalse(stylo.form_dict.pwd)
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		stylo.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		stylo.form_dict.update({"pwd": "password"})
		self.assertRaises(stylo.AuthenticationError, LoginManager)
		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Failed")

		stylo.local.form_dict = stylo._dict()

	def get_auth_log(self, operation="Login"):
		names = stylo.get_all(
			"Activity Log",
			filters={
				"user": "Administrator",
				"operation": operation,
			},
			order_by="`creation` DESC",
		)

		name = names[0]
		auth_log = stylo.get_doc("Activity Log", name)
		return auth_log

	def test_brute_security(self):
		update_system_settings({"allow_consecutive_login_attempts": 3, "allow_login_after_fail": 5})

		stylo.local.form_dict = stylo._dict(
			{"cmd": "login", "sid": "Guest", "pwd": "admin", "usr": "Administrator"}
		)

		stylo.local.request_ip = "127.0.0.1"
		stylo.local.cookie_manager = CookieManager()
		stylo.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		stylo.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		stylo.form_dict.update({"pwd": "password"})
		self.assertRaises(stylo.AuthenticationError, LoginManager)
		self.assertRaises(stylo.AuthenticationError, LoginManager)
		self.assertRaises(stylo.AuthenticationError, LoginManager)

		# REMOVE ME: current logic allows allow_consecutive_login_attempts+1 attempts
		# before raising security exception, remove below line when that is fixed.
		self.assertRaises(stylo.AuthenticationError, LoginManager)
		self.assertRaises(stylo.SecurityException, LoginManager)
		time.sleep(5)
		self.assertRaises(stylo.AuthenticationError, LoginManager)

		stylo.local.form_dict = stylo._dict()


def update_system_settings(args):
	doc = stylo.get_doc("System Settings")
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
