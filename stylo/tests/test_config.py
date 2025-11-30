# Copyright (c) 2022, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.config import get_modules_from_all_apps_for_user
from stylo.tests.utils import StyloTestCase


class TestConfig(StyloTestCase):
	def test_get_modules(self):
		stylo_modules = stylo.get_all("Module Def", filters={"app_name": "stylo"}, pluck="name")
		all_modules_data = get_modules_from_all_apps_for_user()
		first_module_entry = all_modules_data[0]
		all_modules = [x["module_name"] for x in all_modules_data]
		self.assertIn("links", first_module_entry)
		self.assertIsInstance(all_modules_data, list)
		self.assertFalse([x for x in stylo_modules if x not in all_modules])
