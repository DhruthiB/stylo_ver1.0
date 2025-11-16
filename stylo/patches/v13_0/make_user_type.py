import stylo
from stylo.utils.install import create_user_type


def execute():
	stylo.reload_doc("core", "doctype", "role")
	stylo.reload_doc("core", "doctype", "user_document_type")
	stylo.reload_doc("core", "doctype", "user_type_module")
	stylo.reload_doc("core", "doctype", "user_select_document_type")
	stylo.reload_doc("core", "doctype", "user_type")

	create_user_type()
