# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# pre loaded

import stylo
from stylo.tests.utils import StyloTestCase


class TestUser(StyloTestCase):
	def test_default_currency_on_setup(self):
		usd = stylo.get_doc("Currency", "USD")
		self.assertDocumentEqual({"enabled": 1, "fraction": "Cent"}, usd)
