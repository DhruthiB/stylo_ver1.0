# Copyright (c) 2024, Stylo Technologies and Contributors
# See license.txt

import stylo
from stylo.tests.utils import StyloTestCase


class TestSystemHealthReport(StyloTestCase):
	def test_it_works(self):
		stylo.get_doc("System Health Report")
