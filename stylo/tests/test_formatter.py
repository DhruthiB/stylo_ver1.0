import stylo
from stylo import format
from stylo.tests.utils import StyloTestCase


class TestFormatter(StyloTestCase):
	def test_currency_formatting(self):
		df = stylo._dict({"fieldname": "amount", "fieldtype": "Currency", "options": "currency"})

		doc = stylo._dict({"amount": 5})
		stylo.db.set_default("currency", "INR")

		# if currency field is not passed then default currency should be used.
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "₹ 100,000.00")

		doc.currency = "USD"
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "$ 100,000.00")

		stylo.db.set_default("currency", None)
