# Copyright (c) 2020, Stylo Technologies and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.core.doctype.installed_applications.installed_applications import (
	InvalidAppOrder,
	update_installed_apps_order,
)
from frappe.tests.utils import StyloTestCase


class TestInstalledApplications(StyloTestCase):
	def test_order_change(self):
		update_installed_apps_order(["frappe"])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, [])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, ["frappe", "deepmind"])
