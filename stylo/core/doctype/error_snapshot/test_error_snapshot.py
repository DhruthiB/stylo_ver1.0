# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
from stylo.tests.utils import StyloTestCase
from stylo.utils.logger import sanitized_dict

# test_records = stylo.get_test_records('Error Snapshot')


class TestErrorSnapshot(StyloTestCase):
	def test_form_dict_sanitization(self):
		self.assertNotEqual(sanitized_dict({"pwd": "SECRET", "usr": "WHAT"}).get("pwd"), "SECRET")
