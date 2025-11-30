# Copyright (c) 2019, Stylo Technologies and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.config import get_modules_from_all_apps_for_user
from stylo.core.doctype.user.test_user import test_user
from stylo.tests.utils import StyloTestCase


class TestDashboard(StyloTestCase):
	def test_permission_query(self):
		for user in ["Administrator", "test@example.com"]:
			with self.set_user(user):
				stylo.get_list("Dashboard")

		with test_user(roles=["_Test Role"]) as user:
			with self.set_user(user.name):
				stylo.get_list("Dashboard")
				with self.set_user("Administrator"):
					all_modules = get_modules_from_all_apps_for_user("Administrator")
					for module in all_modules:
						user.append("block_modules", {"module": module.get("module_name")})
					user.save()
				stylo.get_list("Dashboard")
