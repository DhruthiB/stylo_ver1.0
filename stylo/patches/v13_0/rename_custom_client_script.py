import stylo
from stylo.model.rename_doc import rename_doc


def execute():
	if stylo.db.exists("DocType", "Client Script"):
		return

	stylo.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "Custom Script", "Client Script")
	stylo.flags.ignore_route_conflict_validation = False

	stylo.reload_doctype("Client Script", force=True)
