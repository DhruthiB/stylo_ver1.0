# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.tests.utils import StyloTestCase

test_records = stylo.get_test_records("Page")


class TestPage(StyloTestCase):
	def test_naming(self):
		self.assertRaises(
			stylo.NameError,
			stylo.get_doc(dict(doctype="Page", page_name="DocType", module="Core")).insert,
		)
		self.assertRaises(
			stylo.NameError,
			stylo.get_doc(dict(doctype="Page", page_name="Settings", module="Core")).insert,
		)
