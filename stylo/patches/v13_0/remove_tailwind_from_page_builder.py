# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	stylo.reload_doc("website", "doctype", "web_page_block")
	# remove unused templates
	stylo.delete_doc("Web Template", "Navbar with Links on Right", force=1)
	stylo.delete_doc("Web Template", "Footer Horizontal", force=1)
