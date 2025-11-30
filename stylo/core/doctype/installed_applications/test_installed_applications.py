# Copyright (c) 2020, Stylo Technologies and Contributors
# License: MIT. See LICENSE

import stylo
from stylo.core.doctype.installed_applications.installed_applications import (
	InvalidAppOrder,
	update_installed_apps_order,
)
from stylo.tests.utils import StyloTestCase


class TestInstalledApplications(StyloTestCase):
	def test_order_change(self):
		update_installed_apps_order(["stylo"])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, [])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, ["stylo", "deepmind"])
