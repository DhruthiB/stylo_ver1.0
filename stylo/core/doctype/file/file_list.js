stylo.listview_settings["File"] = {
	formatters: {
		file_name: function (value) {
			return stylo.utils.escape_html(value || "");
		},
	},
};
