# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	"""Enable all the existing Client script"""

	stylo.db.sql(
		"""
		UPDATE `tabClient Script` SET enabled=1
	"""
	)
