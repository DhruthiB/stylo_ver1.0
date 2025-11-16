import stylo
from stylo.utils.install import add_standard_navbar_items


def execute():
	# Add standard navbar items for ERPNext in Navbar Settings
	stylo.reload_doc("core", "doctype", "navbar_settings")
	stylo.reload_doc("core", "doctype", "navbar_item")
	add_standard_navbar_items()
