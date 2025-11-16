import stylo
from stylo.model.rename_doc import rename_doc


def execute():
	if stylo.db.table_exists("Standard Reply") and not stylo.db.table_exists("Email Template"):
		rename_doc("DocType", "Standard Reply", "Email Template")
		stylo.reload_doc("email", "doctype", "email_template")
