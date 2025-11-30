// Copyright (c) 2019, Stylo Technologies and contributors
// For license information, please see license.txt

stylo.ui.form.on("Personal Data Download Request", {
	onload: function (frm) {
		if (frm.is_new()) {
			frm.doc.user = stylo.session.user;
		}
	},
});
