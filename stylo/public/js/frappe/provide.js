// Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// provide a namespace
if (!window.stylo) window.stylo = {};

stylo.provide = function (namespace) {
	// docs: create a namespace //
	var nsl = namespace.split(".");
	var parent = window;
	for (var i = 0; i < nsl.length; i++) {
		var n = nsl[i];
		if (!parent[n]) {
			parent[n] = {};
		}
		parent = parent[n];
	}
	return parent;
};

stylo.provide("locals");
stylo.provide("stylo.flags");
stylo.provide("stylo.settings");
stylo.provide("stylo.utils");
stylo.provide("stylo.ui.form");
stylo.provide("stylo.modules");
stylo.provide("stylo.templates");
stylo.provide("stylo.test_data");
stylo.provide("stylo.utils");
stylo.provide("stylo.model");
stylo.provide("stylo.user");
stylo.provide("stylo.session");
stylo.provide("stylo._messages");
stylo.provide("locals.DocType");

// for listviews
stylo.provide("stylo.listview_settings");
stylo.provide("stylo.tour");
stylo.provide("stylo.listview_parent_route");

// constants
window.NEWLINE = "\n";
window.TAB = 9;
window.UP_ARROW = 38;
window.DOWN_ARROW = 40;

// proxy for user globals defined in desk.js

// API globals
window.cur_frm = null;
