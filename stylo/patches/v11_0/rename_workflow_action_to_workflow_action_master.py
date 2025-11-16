import stylo
from stylo.model.rename_doc import rename_doc


def execute():
	if stylo.db.table_exists("Workflow Action") and not stylo.db.table_exists("Workflow Action Master"):
		rename_doc("DocType", "Workflow Action", "Workflow Action Master")
		stylo.reload_doc("workflow", "doctype", "workflow_action_master")
