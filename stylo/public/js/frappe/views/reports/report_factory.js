// Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

stylo.views.ReportFactory = class ReportFactory extends stylo.views.Factory {
	make(route) {
		const _route = ["List", route[1], "Report"];

		if (route[2]) {
			// custom report
			_route.push(route[2]);
		}

		stylo.set_route(_route);
	}
};
