# Copyright (c) 2015, Stylo Technologies and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.tests.utils import StyloTestCase

# test_records = stylo.get_test_records('Help Article')


class TestHelpArticle(StyloTestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.help_category = stylo.get_doc(
			{
				"doctype": "Help Category",
				"category_name": "_Test Help Category",
			}
		).insert()

		cls.help_article = stylo.get_doc(
			{
				"doctype": "Help Article",
				"title": "_Test Article",
				"category": cls.help_category.name,
				"content": "_Test Article",
			}
		).insert()

	@classmethod
	def tearDownClass(cls) -> None:
		stylo.delete_doc(cls.help_article.doctype, cls.help_article.name)
		stylo.delete_doc(cls.help_category.doctype, cls.help_category.name)
