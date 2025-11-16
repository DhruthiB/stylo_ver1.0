// Copyright (c) 2024, Stylo Technologies and contributors
// For license information, please see license.txt

stylo.query_reports["User Doctype Permissions"] = {
	filters: [
		{
			fieldname: "user",
			label: __("User"),
			fieldtype: "Link",
			options: "User",
			reqd: 1,
		},
	],
};
