import stylo


def execute():
	stylo.reload_doc("workflow", "doctype", "workflow_transition")
	stylo.db.sql("update `tabWorkflow Transition` set allow_self_approval=1")
