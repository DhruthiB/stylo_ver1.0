// Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

stylo.provide("stylo.pages");
stylo.provide("stylo.views");

stylo.views.Factory = class Factory {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		this.route = stylo.get_route();
		this.page_name = stylo.get_route_str();

		if (this.before_show && this.before_show() === false) return;

		if (stylo.pages[this.page_name]) {
			stylo.container.change_to(this.page_name);
			if (this.on_show) {
				this.on_show();
			}
		} else {
			if (this.route[1]) {
				this.make(this.route);
			} else {
				stylo.show_not_found(this.route);
			}
		}
	}

	make_page(double_column, page_name) {
		return stylo.make_page(double_column, page_name);
	}
};

stylo.make_page = function (double_column, page_name) {
	if (!page_name) {
		page_name = stylo.get_route_str();
	}

	const page = stylo.container.add_page(page_name);

	stylo.ui.make_app_page({
		parent: page,
		single_column: !double_column,
	});

	stylo.container.change_to(page_name);
	return page;
};
