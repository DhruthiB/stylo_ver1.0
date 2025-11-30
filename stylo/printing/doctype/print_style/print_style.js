// Copyright (c) 2017, Stylo Technologies and contributors
// For license information, please see license.txt

stylo.ui.form.on("Print Style", {
	refresh: function (frm) {
		frm.add_custom_button(__("Print Settings"), () => {
			stylo.set_route("Form", "Print Settings");
		});
	},
});
