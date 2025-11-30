stylo.listview_settings["Event"] = {
	add_fields: ["starts_on", "ends_on"],
	onload: function () {
		stylo.route_options = {
			status: "Open",
		};
	},
};
