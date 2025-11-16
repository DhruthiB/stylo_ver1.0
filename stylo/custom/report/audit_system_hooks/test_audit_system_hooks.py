# Copyright (c) 2022, Stylo Technologies and contributors
# For license information, please see license.txt


from stylo.custom.report.audit_system_hooks.audit_system_hooks import execute
from stylo.tests.utils import StyloTestCase


class TestAuditSystemHooksReport(StyloTestCase):
	def test_basic_query(self):
		_, data = execute()
		for row in data:
			if row.get("hook_name") == "app_name":
				self.assertEqual(row.get("hook_values"), "stylo")
				break
		else:
			self.fail("Failed to generate hooks report")
