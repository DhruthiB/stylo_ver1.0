stylo.listview_settings["Scheduled Job Log"] = {
	onload: function (listview) {
		stylo.require("logtypes.bundle.js", () => {
			stylo.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
