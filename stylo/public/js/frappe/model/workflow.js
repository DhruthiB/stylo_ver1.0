// Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

stylo.provide("stylo.workflow");

stylo.workflow = {
	state_fields: {},
	workflows: {},
	avoid_status_override: {},
	setup: function (doctype) {
		var wf = stylo.get_list("Workflow", { document_type: doctype });
		if (wf.length) {
			stylo.workflow.workflows[doctype] = wf[0];
			stylo.workflow.state_fields[doctype] = wf[0].workflow_state_field;
			stylo.workflow.avoid_status_override[doctype] = wf[0].states
				.filter((row) => row.avoid_status_override)
				.map((d) => d.state);
		} else {
			stylo.workflow.state_fields[doctype] = null;
		}
	},
	get_state_fieldname: function (doctype) {
		if (stylo.workflow.state_fields[doctype] === undefined) {
			stylo.workflow.setup(doctype);
		}
		return stylo.workflow.state_fields[doctype];
	},
	get_default_state: function (doctype, docstatus) {
		stylo.workflow.setup(doctype);
		var value = null;
		$.each(stylo.workflow.workflows[doctype].states, function (i, workflow_state) {
			if (cint(workflow_state.doc_status) === cint(docstatus)) {
				value = workflow_state.state;
				return false;
			}
		});
		return value;
	},
	get_transitions: function (doc) {
		stylo.workflow.setup(doc.doctype);
		return stylo.xcall("stylo.model.workflow.get_transitions", { doc: doc });
	},
	get_document_state_roles: function (doctype, state) {
		stylo.workflow.setup(doctype);
		let workflow_states =
			stylo.get_children(stylo.workflow.workflows[doctype], "states", { state: state }) ||
			[];
		let allow_edit_list = workflow_states.map((d) => d.allow_edit);
		return allow_edit_list;
	},
	is_self_approval_enabled: function (doctype) {
		return stylo.workflow.workflows[doctype].allow_self_approval;
	},
	is_read_only: function (doctype, name) {
		var state_fieldname = stylo.workflow.get_state_fieldname(doctype);
		if (state_fieldname) {
			var doc = locals[doctype][name];
			if (!doc) return false;
			if (doc.__islocal) return false;

			var state =
				doc[state_fieldname] || stylo.workflow.get_default_state(doctype, doc.docstatus);
			if (!state) return false;

			let allow_edit_roles = stylo.workflow.get_document_state_roles(doctype, state);
			let has_common_role = stylo.user_roles.some((role) =>
				allow_edit_roles.includes(role)
			);
			return !has_common_role;
		}
		return false;
	},
	get_update_fields: function (doctype) {
		var update_fields = $.unique(
			$.map(stylo.workflow.workflows[doctype].states || [], function (d) {
				return d.update_field;
			})
		);
		return update_fields;
	},
	get_state(doc) {
		const state_field = this.get_state_fieldname(doc.doctype);
		let state = doc[state_field];
		if (!state) {
			state = this.get_default_state(doc.doctype, doc.docstatus);
		}
		return state;
	},
	get_all_transitions(doctype) {
		return stylo.workflow.workflows[doctype].transitions || [];
	},
	get_all_transition_actions(doctype) {
		const transitions = this.get_all_transitions(doctype);
		return transitions.map((transition) => {
			return transition.action;
		});
	},
};
