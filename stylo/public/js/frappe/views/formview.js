// Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

stylo.provide("stylo.views.formview");

stylo.views.FormFactory = class FormFactory extends stylo.views.Factory {
	make(route) {
		var doctype = route[1],
			doctype_layout = stylo.router.doctype_layout || doctype;

		if (!stylo.views.formview[doctype_layout]) {
			stylo.model.with_doctype(doctype, () => {
				this.page = stylo.container.add_page(doctype_layout);
				stylo.views.formview[doctype_layout] = this.page;
				this.make_and_show(doctype, route);
			});
		} else {
			this.show_doc(route);
		}

		this.setup_events();
	}

	make_and_show(doctype, route) {
		if (stylo.router.doctype_layout) {
			stylo.model.with_doc("DocType Layout", stylo.router.doctype_layout, () => {
				this.make_form(doctype);
				this.show_doc(route);
			});
		} else {
			this.make_form(doctype);
			this.show_doc(route);
		}
	}

	make_form(doctype) {
		this.page.frm = new stylo.ui.form.Form(
			doctype,
			this.page,
			true,
			stylo.router.doctype_layout
		);
	}

	setup_events() {
		if (!this.initialized) {
			$(document).on("page-change", function () {
				stylo.ui.form.close_grid_form();
			});

			stylo.realtime.on("doc_viewers", function (data) {
				// set users that currently viewing the form
				stylo.ui.form.FormViewers.set_users(data, "viewers");
			});

			stylo.realtime.on("doc_typers", function (data) {
				// set users that currently typing on the form
				stylo.ui.form.FormViewers.set_users(data, "typers");
			});
		}
		this.initialized = true;
	}

	show_doc(route) {
		var doctype = route[1],
			doctype_layout = stylo.router.doctype_layout || doctype,
			name = route.slice(2).join("/");

		if (stylo.model.new_names[name]) {
			// document has been renamed, reroute
			name = stylo.model.new_names[name];
			stylo.set_route("Form", doctype_layout, name);
			return;
		}

		const doc = stylo.get_doc(doctype, name);
		if (
			doc &&
			stylo.model.get_docinfo(doctype, name) &&
			(doc.__islocal || stylo.model.is_fresh(doc))
		) {
			// is document available and recent?
			this.render(doctype_layout, name);
		} else {
			this.fetch_and_render(doctype, name, doctype_layout);
		}
	}

	fetch_and_render(doctype, name, doctype_layout) {
		stylo.model.with_doc(doctype, name, (name, r) => {
			if (r && r["403"]) return; // not permitted

			if (!(locals[doctype] && locals[doctype][name])) {
				if (name && name.substr(0, 3) === "new") {
					this.render_new_doc(doctype, name, doctype_layout);
				} else {
					stylo.show_not_found();
				}
				return;
			}
			this.render(doctype_layout, name);
		});
	}

	render_new_doc(doctype, name, doctype_layout) {
		const new_name = stylo.model.make_new_doc_and_get_name(doctype, true);
		if (new_name === name) {
			this.render(doctype_layout, name);
		} else {
			stylo.route_flags.replace_route = true;
			stylo.set_route("Form", doctype_layout, new_name);
		}
	}

	render(doctype_layout, name) {
		stylo.container.change_to(doctype_layout);
		stylo.views.formview[doctype_layout].frm.refresh(name);
	}
};
