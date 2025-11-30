# Copyright (c) 2020, Stylo Technologies and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.tests.utils import StyloTestCase


class TestModuleProfile(StyloTestCase):
	def test_make_new_module_profile(self):
		if not stylo.db.get_value("Module Profile", "_Test Module Profile"):
			stylo.get_doc(
				{
					"doctype": "Module Profile",
					"module_profile_name": "_Test Module Profile",
					"block_modules": [{"module": "Accounts"}],
				}
			).insert()

		# add to user and check
		if not stylo.db.get_value("User", "test-for-module_profile@example.com"):
			new_user = stylo.get_doc(
				{"doctype": "User", "email": "test-for-module_profile@example.com", "first_name": "Test User"}
			).insert()
		else:
			new_user = stylo.get_doc("User", "test-for-module_profile@example.com")

		new_user.module_profile = "_Test Module Profile"
		new_user.save()

		self.assertEqual(new_user.block_modules[0].module, "Accounts")
