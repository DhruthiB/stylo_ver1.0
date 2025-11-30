// Copyright (c) 2022, Stylo Technologies and contributors
// For license information, please see license.txt

stylo.ui.form.on("RQ Job", {
	refresh: function (frm) {
		// Nothing in this form is supposed to be editable.
		frm.disable_form();
		frm.dashboard.set_headline_alert(
			"This is a virtual doctype and data is cleared periodically."
		);

		if (["started", "queued"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Force Stop job"), () => {
				stylo.confirm(
					"This will terminate the job immediately and might be dangerous, are you sure? ",
					() => {
						stylo
							.xcall("stylo.core.doctype.rq_job.rq_job.stop_job", {
								job_id: frm.doc.name,
							})
							.then((r) => {
								stylo.show_alert("Job Stopped Succefully");
								frm.reload_doc();
							});
					}
				);
			});
		}
	},
});
