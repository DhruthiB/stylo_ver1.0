stylo.pages["backups"].on_page_load = function (wrapper) {
	var page = stylo.ui.make_app_page({
		parent: wrapper,
		title: __("Download Backups"),
		single_column: true,
	});

	page.add_inner_button(__("Set Number of Backups"), function () {
		stylo.set_route("Form", "System Settings");
	});

	page.add_inner_button(__("Download Files Backup"), function () {
		stylo.call({
			method: "stylo.desk.page.backups.backups.schedule_files_backup",
			args: { user_email: stylo.session.user_email },
		});
	});

	page.add_inner_button(__("Get Backup Encryption Key"), function () {
		if (stylo.user.has_role("System Manager")) {
			stylo.verify_password(function () {
				stylo.call({
					method: "stylo.utils.backups.get_backup_encryption_key",
					callback: function (r) {
						stylo.msgprint({
							title: __("Backup Encryption Key"),
							message: __(r.message),
							indicator: "blue",
						});
					},
				});
			});
		} else {
			stylo.msgprint({
				title: __("Error"),
				message: __("System Manager privileges required."),
				indicator: "red",
			});
		}
	});

	stylo.breadcrumbs.add("Setup");

	$(stylo.render_template("backups")).appendTo(page.body.addClass("no-border"));
};
