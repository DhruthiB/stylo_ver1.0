// Copyright (c) 2017, Stylo Technologies and contributors
// For license information, please see license.txt

stylo.ui.form.on("Activity Log", {
	refresh: function (frm) {
		// Nothing in this form is supposed to be editable.
		frm.disable_form();
	},
});
