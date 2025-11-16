# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	if stylo.db.exists("DocType", "Event Producer"):
		stylo.db.sql("""UPDATE `tabEvent Producer` SET api_key='', api_secret=''""")
	if stylo.db.exists("DocType", "Event Consumer"):
		stylo.db.sql("""UPDATE `tabEvent Consumer` SET api_key='', api_secret=''""")
