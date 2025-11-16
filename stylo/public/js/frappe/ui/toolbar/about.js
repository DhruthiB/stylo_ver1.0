stylo.provide("stylo.ui.misc");
stylo.ui.misc.about = function () {
	if (!stylo.ui.misc.about_dialog) {
		var d = new stylo.ui.Dialog({ title: __("Stylo Framework") });

		$(d.body).html(
			repl(
				"<div>\
		<p>" +
					__("Open Source Applications for the Web") +
					"</p>  \
		<p><i class='fa fa-globe fa-fw'></i>\
			Website: <a href='https://styloframework.com' target='_blank'>https://styloframework.com</a></p>\
		<p><i class='fa fa-github fa-fw'></i>\
			Source: <a href='https://github.com/stylo' target='_blank'>https://github.com/stylo</a></p>\
		<p><i class='fa fa-linkedin fa-fw'></i>\
			Linkedin: <a href='https://linkedin.com/company/stylo-tech' target='_blank'>https://linkedin.com/company/stylo-tech</a></p>\
		<p><i class='fa fa-facebook fa-fw'></i>\
			Facebook: <a href='https://facebook.com/erpnext' target='_blank'>https://facebook.com/erpnext</a></p>\
		<p><i class='fa fa-twitter fa-fw'></i>\
			Twitter: <a href='https://twitter.com/erpnext' target='_blank'>https://twitter.com/erpnext</a></p>\
		<hr>\
		<h4>Installed Apps</h4>\
		<div id='about-app-versions'>Loading versions...</div>\
		<hr>\
		<p class='text-muted'>&copy; Stylo Technologies Pvt. Ltd. and contributors </p> \
		</div>",
				stylo.app
			)
		);

		stylo.ui.misc.about_dialog = d;

		stylo.ui.misc.about_dialog.on_page_show = function () {
			if (!stylo.versions) {
				stylo.call({
					method: "stylo.utils.change_log.get_versions",
					callback: function (r) {
						show_versions(r.message);
					},
				});
			} else {
				show_versions(stylo.versions);
			}
		};

		var show_versions = function (versions) {
			var $wrap = $("#about-app-versions").empty();
			$.each(Object.keys(versions).sort(), function (i, key) {
				var v = versions[key];
				if (v.branch) {
					var text = $.format("<p><b>{0}:</b> v{1} ({2})<br></p>", [
						v.title,
						v.branch_version || v.version,
						v.branch,
					]);
				} else {
					var text = $.format("<p><b>{0}:</b> v{1}<br></p>", [v.title, v.version]);
				}
				$(text).appendTo($wrap);
			});

			stylo.versions = versions;
		};
	}

	stylo.ui.misc.about_dialog.show();
};
