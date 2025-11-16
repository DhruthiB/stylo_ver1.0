# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os
import unittest
from unittest.mock import patch

import stylo
from stylo.tests import IntegrationTestCase


class TestPage(IntegrationTestCase):
	def test_naming(self):
		self.assertRaises(
			stylo.NameError,
			stylo.get_doc(doctype="Page", page_name="DocType", module="Core").insert,
		)

	@unittest.skipUnless(
		os.access(stylo.get_app_path("stylo"), os.W_OK), "Only run if stylo app paths is writable"
	)
	@patch.dict(stylo.conf, {"developer_mode": 1})
	def test_trashing(self):
		page = stylo.new_doc("Page", page_name=stylo.generate_hash(), module="Core").insert()

		page.delete()
		stylo.db.commit()

		module_path = stylo.get_module_path(page.module)
		dir_path = os.path.join(module_path, "page", stylo.scrub(page.name))

		self.assertFalse(os.path.exists(dir_path))
