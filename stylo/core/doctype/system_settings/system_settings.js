stylo.ui.form.on("System Settings", {
	refresh: function (frm) {
		stylo.call({
			method: "stylo.core.doctype.system_settings.system_settings.load",
			callback: function (data) {
				stylo.all_timezones = data.message.timezones;
				frm.set_df_property("time_zone", "options", stylo.all_timezones);

				$.each(data.message.defaults, function (key, val) {
					frm.set_value(key, val, null, true);
					stylo.sys_defaults[key] = val;
				});
				if (frm.re_setup_moment) {
					stylo.app.setup_moment();
					delete frm.re_setup_moment;
				}
			},
		});
	},
	enable_password_policy: function (frm) {
		if (frm.doc.enable_password_policy == 0) {
			frm.set_value("minimum_password_score", "");
		} else {
			frm.set_value("minimum_password_score", "2");
		}
	},
	enable_two_factor_auth: function (frm) {
		if (frm.doc.enable_two_factor_auth == 0) {
			frm.set_value("bypass_2fa_for_retricted_ip_users", 0);
			frm.set_value("bypass_restrict_ip_check_if_2fa_enabled", 0);
		}
	},
	on_update: function (frm) {
		if (stylo.boot.time_zone && stylo.boot.time_zone.system !== frm.doc.time_zone) {
			// Clear cache after saving to refresh the values of boot.
			stylo.ui.toolbar.clear_cache();
		}
	},
	first_day_of_the_week(frm) {
		frm.re_setup_moment = true;
	},

	rounding_method: function (frm) {
		if (frm.doc.rounding_method == stylo.boot.sysdefaults.rounding_method) return;
		let msg = __(
			"Changing rounding method on site with data can result in unexpected behaviour."
		);
		msg += "<br>";
		msg += __("Do you still want to proceed?");

		stylo.confirm(
			msg,
			() => {},
			() => {
				frm.set_value("rounding_method", stylo.boot.sysdefaults.rounding_method);
			}
		);
	},
});
