# Copyright (c) 2017, Stylo Technologies and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.tests.utils import StyloTestCase


class TestLetterHead(StyloTestCase):
	def test_auto_image(self):
		letter_head = stylo.get_doc(
			dict(doctype="Letter Head", letter_head_name="Test", source="Image", image="/public/test.png")
		).insert()

		# test if image is automatically set
		self.assertTrue(letter_head.image in letter_head.content)
