// Copyright (c) 2025, Stylo Technologies and contributors
// For license information, please see license.txt

stylo.ui.form.on("Workflow Transition Tasks", {
	refresh: function (frm) {
		stylo
			.call({
				method: "stylo.workflow.doctype.workflow.workflow.get_workflow_methods",
				type: "GET",
			})
			.then((options) => {
				frm.get_field("tasks").grid.update_docfield_property(
					"task",
					"options",
					options.message
				);
			});
	},
});
