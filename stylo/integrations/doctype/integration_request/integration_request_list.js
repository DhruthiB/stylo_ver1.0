stylo.listview_settings["Integration Request"] = {
	onload: function (list_view) {
		stylo.require("logtypes.bundle.js", () => {
			stylo.utils.logtypes.show_log_retention_message(list_view.doctype);
		});
	},
};
