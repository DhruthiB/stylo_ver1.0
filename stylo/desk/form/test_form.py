# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo
from stylo.desk.form.linked_with import get_linked_docs, get_linked_doctypes
from stylo.tests.utils import StyloTestCase


class TestForm(StyloTestCase):
	def test_linked_with(self):
		results = get_linked_docs("Role", "System Manager", linkinfo=get_linked_doctypes("Role"))
		self.assertTrue("User" in results)
		self.assertTrue("DocType" in results)


if __name__ == "__main__":
	import unittest

	stylo.connect()
	unittest.main()
