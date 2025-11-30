stylo.listview_settings["Notification Log"] = {
	onload: function (listview) {
		stylo.require("logtypes.bundle.js", () => {
			stylo.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
