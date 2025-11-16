import stylo
from stylo.model.rename_doc import rename_doc


def execute():
	if stylo.db.exists("DocType", "Google Maps") and not stylo.db.exists("DocType", "Google Maps Settings"):
		rename_doc("DocType", "Google Maps", "Google Maps Settings")
