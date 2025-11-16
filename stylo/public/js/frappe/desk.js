// Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt
/* eslint-disable no-console */

// __('Modules') __('Domains') __('Places') __('Administration') # for translation, don't remove

stylo.start_app = function () {
	if (!stylo.Application) return;
	stylo.assets.check();
	stylo.provide("stylo.app");
	stylo.provide("stylo.desk");
	stylo.app = new stylo.Application();
};

$(document).ready(function () {
	if (!stylo.utils.supportsES6) {
		stylo.msgprint({
			indicator: "red",
			title: __("Browser not supported"),
			message: __(
				"Some of the features might not work in your browser. Please update your browser to the latest version."
			),
		});
	}
	stylo.start_app();
});

stylo.Application = class Application {
	constructor() {
		this.startup();
	}

	startup() {
		stylo.realtime.init();
		stylo.model.init();

		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.make_sidebar();
		this.set_favicon();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_copy_doc_listener();
		this.setup_broadcast_listeners();

		stylo.ui.keys.setup();

		this.setup_theme();

		// page container
		this.make_page_container();
		this.setup_tours();
		this.set_route();

		// trigger app startup
		$(document).trigger("startup");
		$(document).trigger("app_ready");

		this.show_notices();
		this.show_notes();

		if (stylo.ui.startup_setup_dialog && !stylo.boot.setup_complete) {
			stylo.ui.startup_setup_dialog.pre_show();
			stylo.ui.startup_setup_dialog.show();
		}

		// listen to build errors
		this.setup_build_events();

		if (stylo.sys_defaults.email_user_password) {
			var email_list = stylo.sys_defaults.email_user_password.split(",");
			for (var u in email_list) {
				if (email_list[u] === stylo.user.name) {
					this.set_password(email_list[u]);
				}
			}
		}

		// REDESIGN-TODO: Fix preview popovers
		this.link_preview = new stylo.ui.LinkPreview();

		stylo.broadcast.emit("boot", {
			csrf_token: stylo.csrf_token,
			user: stylo.session.user,
		});
	}

	make_sidebar() {
		this.sidebar = new stylo.ui.Sidebar({});
	}

	setup_theme() {
		stylo.ui.keys.add_shortcut({
			shortcut: "shift+ctrl+g",
			description: __("Switch Theme"),
			action: () => {
				if (stylo.theme_switcher && stylo.theme_switcher.dialog.is_visible) {
					stylo.theme_switcher.hide();
				} else {
					stylo.theme_switcher = new stylo.ui.ThemeSwitcher();
					stylo.theme_switcher.show();
				}
			},
		});

		stylo.ui.add_system_theme_switch_listener();
		const root = document.documentElement;

		const observer = new MutationObserver(() => {
			stylo.ui.set_theme();
		});
		observer.observe(root, {
			attributes: true,
			attributeFilter: ["data-theme-mode"],
		});

		stylo.ui.set_theme();
	}

	setup_tours() {
		if (
			!window.Cypress &&
			stylo.boot.onboarding_tours &&
			stylo.boot.user.onboarding_status != null
		) {
			let pending_tours = !stylo.boot.onboarding_tours.every(
				(tour) => stylo.boot.user.onboarding_status[tour[0]]?.is_complete
			);
			if (pending_tours && stylo.boot.onboarding_tours.length > 0) {
				stylo.require("onboarding_tours.bundle.js", () => {
					stylo.utils.sleep(1000).then(() => {
						stylo.ui.init_onboarding_tour();
					});
				});
			}
		}
	}

	show_notices() {
		if (stylo.boot.messages) {
			stylo.msgprint(stylo.boot.messages);
		}

		if (stylo.user_roles.includes("System Manager")) {
			// delayed following requests to make boot faster
			setTimeout(() => {
				this.show_change_log();
				this.show_update_available();
			}, 1000);
		}

		if (!stylo.boot.developer_mode) {
			let console_security_message = __(
				"Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand."
			);
			console.log(`%c${console_security_message}`, "font-size: large");
		}

		stylo.realtime.on("version-update", function () {
			var dialog = stylo.msgprint({
				message: __(
					"The application has been updated to a new version, please refresh this page"
				),
				indicator: "green",
				title: __("Version Updated"),
			});
			dialog.set_primary_action(__("Refresh"), function () {
				location.reload(true);
			});
			dialog.get_close_btn().toggle(false);
		});
	}

	set_route() {
		if (stylo.boot && localStorage.getItem("session_last_route")) {
			stylo.set_route(localStorage.getItem("session_last_route"));
			localStorage.removeItem("session_last_route");
		} else {
			// route to home page
			stylo.router.route();
		}
		stylo.router.on("change", () => {
			$(".tooltip").hide();
			if (stylo.stylo_toolbar && stylo.is_mobile()) stylo.stylo_toolbar.show_app_logo();
		});
	}

	set_password(user) {
		var me = this;
		stylo.call({
			method: "stylo.core.doctype.user.user.get_email_awaiting",
			args: {
				user: user,
			},
			callback: function (email_account) {
				email_account = email_account["message"];
				if (email_account) {
					var i = 0;
					if (i < email_account.length) {
						me.email_password_prompt(email_account, user, i);
					}
				}
			},
		});
	}

	email_password_prompt(email_account, user, i) {
		var me = this;
		const email_id = email_account[i]["email_id"];
		let d = new stylo.ui.Dialog({
			title: __("Password missing in Email Account"),
			fields: [
				{
					fieldname: "password",
					fieldtype: "Password",
					label: __(
						"Please enter the password for: <b>{0}</b>",
						[email_id],
						"Email Account"
					),
					reqd: 1,
				},
				{
					fieldname: "submit",
					fieldtype: "Button",
					label: __("Submit", null, "Submit password for Email Account"),
				},
			],
		});
		d.get_input("submit").on("click", function () {
			//setup spinner
			d.hide();
			var s = new stylo.ui.Dialog({
				title: __("Checking one moment"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "checking",
					},
				],
			});
			s.fields_dict.checking.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
			s.show();
			stylo.call({
				method: "stylo.email.doctype.email_account.email_account.set_email_password",
				args: {
					email_account: email_account[i]["email_account"],
					password: d.get_value("password"),
				},
				callback: function (passed) {
					s.hide();
					d.hide(); //hide waiting indication
					if (!passed["message"]) {
						stylo.show_alert(
							{ message: __("Login Failed please try again"), indicator: "error" },
							5
						);
						me.email_password_prompt(email_account, user, i);
					} else {
						if (i + 1 < email_account.length) {
							i = i + 1;
							me.email_password_prompt(email_account, user, i);
						}
					}
				},
			});
		});
		d.show();
	}
	load_bootinfo() {
		if (stylo.boot) {
			this.setup_workspaces();
			stylo.model.sync(stylo.boot.docs);
			this.check_metadata_cache_status();
			this.set_globals();
			this.sync_pages();
			stylo.router.setup();
			this.setup_moment();
			if (stylo.boot.print_css) {
				stylo.dom.set_style(stylo.boot.print_css, "print-style");
			}

			stylo.boot.setup_complete = stylo.boot.sysdefaults["setup_complete"];
			stylo.user.name = stylo.boot.user.name;
			stylo.router.setup();
		} else {
			this.set_as_guest();
		}
	}

	setup_workspaces() {
		stylo.modules = {};
		stylo.workspaces = {};
		stylo.boot.allowed_workspaces = stylo.boot.sidebar_pages.pages;

		for (let page of stylo.boot.allowed_workspaces || []) {
			stylo.modules[page.module] = page;
			stylo.workspaces[stylo.router.slug(page.name)] = page;
		}
	}

	load_user_permissions() {
		stylo.defaults.load_user_permission_from_boot();

		stylo.realtime.on(
			"update_user_permissions",
			stylo.utils.debounce(() => {
				stylo.defaults.update_user_permissions();
			}, 500)
		);
	}

	check_metadata_cache_status() {
		if (stylo.boot.metadata_version != localStorage.metadata_version) {
			stylo.assets.clear_local_storage();
			stylo.assets.init_local_storage();
		}
	}

	set_globals() {
		stylo.session.user = stylo.boot.user.name;
		stylo.session.logged_in_user = stylo.boot.user.name;
		stylo.session.user_email = stylo.boot.user.email;
		stylo.session.user_fullname = stylo.user_info().fullname;

		stylo.user_defaults = stylo.boot.user.defaults;
		stylo.user_roles = stylo.boot.user.roles;
		stylo.sys_defaults = stylo.boot.sysdefaults;

		stylo.ui.py_date_format = stylo.boot.sysdefaults.date_format
			.replace("dd", "%d")
			.replace("mm", "%m")
			.replace("yyyy", "%Y");
		stylo.boot.user.last_selected_values = {};
	}
	sync_pages() {
		// clear cached pages if timestamp is not found
		if (localStorage["page_info"]) {
			stylo.boot.allowed_pages = [];
			var page_info = JSON.parse(localStorage["page_info"]);
			$.each(stylo.boot.page_info, function (name, p) {
				if (!page_info[name] || page_info[name].modified != p.modified) {
					delete localStorage["_page:" + name];
				}
				stylo.boot.allowed_pages.push(name);
			});
		} else {
			stylo.boot.allowed_pages = Object.keys(stylo.boot.page_info);
		}
		localStorage["page_info"] = JSON.stringify(stylo.boot.page_info);
	}
	set_as_guest() {
		stylo.session.user = "Guest";
		stylo.session.user_email = "";
		stylo.session.user_fullname = "Guest";

		stylo.user_defaults = {};
		stylo.user_roles = ["Guest"];
		stylo.sys_defaults = {};
	}
	make_page_container() {
		if ($("#body").length) {
			$(".splash").remove();
			stylo.temp_container = $("<div id='temp-container' style='display: none;'>").appendTo(
				"body"
			);
			stylo.container = new stylo.views.Container();
		}
	}
	make_nav_bar() {
		// toolbar
		if (stylo.boot && stylo.boot.home_page !== "setup-wizard") {
			stylo.stylo_toolbar = new stylo.ui.toolbar.Toolbar();
		}
	}
	logout() {
		var me = this;
		me.logged_out = true;
		return stylo.call({
			method: "logout",
			callback: function (r) {
				if (r.exc) {
					return;
				}

				me.redirect_to_login();
			},
		});
	}
	handle_session_expired() {
		stylo.app.redirect_to_login();
	}
	redirect_to_login() {
		window.location.href = `/login?redirect-to=${encodeURIComponent(
			window.location.pathname + window.location.search
		)}`;
	}
	set_favicon() {
		var link = $('link[type="image/x-icon"]').remove().attr("href");
		$('<link rel="shortcut icon" href="' + link + '" type="image/x-icon">').appendTo("head");
		$('<link rel="icon" href="' + link + '" type="image/x-icon">').appendTo("head");
	}
	trigger_primary_action() {
		// to trigger change event on active input before triggering primary action
		$(document.activeElement).blur();
		// wait for possible JS validations triggered after blur (it might change primary button)
		setTimeout(() => {
			if (window.cur_dialog && cur_dialog.display && !cur_dialog.is_minimized) {
				// trigger primary
				cur_dialog.get_primary_btn().trigger("click");
			} else if (cur_frm && cur_frm.page.btn_primary.is(":visible")) {
				cur_frm.page.btn_primary.trigger("click");
			} else if (stylo.container.page.save_action) {
				stylo.container.page.save_action();
			}
		}, 100);
	}

	show_change_log() {
		var me = this;
		let change_log = stylo.boot.change_log;

		// stylo.boot.change_log = [{
		// 	"change_log": [
		// 		[<version>, <change_log in markdown>],
		// 		[<version>, <change_log in markdown>],
		// 	],
		// 	"description": "ERP made simple",
		// 	"title": "ERPNext",
		// 	"version": "12.2.0"
		// }];

		if (
			!Array.isArray(change_log) ||
			!change_log.length ||
			window.Cypress ||
			cint(stylo.boot.sysdefaults.disable_change_log_notification)
		) {
			return;
		}

		// Iterate over changelog
		var change_log_dialog = stylo.msgprint({
			message: stylo.render_template("change_log", { change_log: change_log }),
			title: __("Updated To A New Version 🎉"),
			wide: true,
		});
		change_log_dialog.keep_open = true;
		change_log_dialog.custom_onhide = function () {
			stylo.call({
				method: "stylo.utils.change_log.update_last_known_versions",
			});
			me.show_notes();
		};
	}

	show_update_available() {
		if (!stylo.boot.has_app_updates) return;
		stylo.xcall("stylo.utils.change_log.show_update_popup");
	}

	add_browser_class() {
		$("html").addClass(stylo.utils.get_browser().name.toLowerCase());
	}

	set_fullwidth_if_enabled() {
		stylo.ui.toolbar.set_fullwidth_if_enabled();
	}

	show_notes() {
		var me = this;
		if (stylo.boot.notes.length) {
			stylo.boot.notes.forEach(function (note) {
				if (!note.seen || note.notify_on_every_login) {
					var d = new stylo.ui.Dialog({ content: note.content, title: note.title });
					d.keep_open = true;
					d.msg_area = $('<div class="msgprint">').appendTo(d.body);
					d.msg_area.append(note.content);
					d.onhide = function () {
						note.seen = true;
						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							stylo.call({
								method: "stylo.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name,
								},
							});
						} else {
							stylo.call({
								method: "stylo.desk.doctype.note.note.reset_notes",
							});
						}
					};
					d.show();
				}
			});
		}
	}

	setup_build_events() {
		if (stylo.boot.developer_mode) {
			stylo.require("build_events.bundle.js");
		}
	}

	setup_copy_doc_listener() {
		$("body").on("paste", (e) => {
			try {
				let pasted_data = stylo.utils.get_clipboard_data(e);
				let doc = JSON.parse(pasted_data);
				if (doc.doctype) {
					e.preventDefault();
					const sleep = stylo.utils.sleep;

					stylo.dom.freeze(__("Creating {0}", [doc.doctype]) + "...");
					// to avoid abrupt UX
					// wait for activity feedback
					sleep(500).then(() => {
						let res = stylo.model.with_doctype(doc.doctype, () => {
							let newdoc = stylo.model.copy_doc(doc);
							newdoc.__newname = doc.name;
							delete doc.name;
							newdoc.idx = null;
							newdoc.__run_link_triggers = false;
							newdoc.on_paste_event = true;
							newdoc = JSON.parse(JSON.stringify(newdoc));
							stylo.set_route("Form", newdoc.doctype, newdoc.name);
							stylo.dom.unfreeze();
						});
						res && res.fail?.(stylo.dom.unfreeze);
					});
				}
			} catch (e) {
				//
			}
		});
	}

	/// Setup event listeners for events across browser tabs / web workers.
	setup_broadcast_listeners() {
		// booted in another tab -> refresh csrf to avoid invalid requests.
		stylo.broadcast.on("boot", ({ csrf_token, user }) => {
			if (user && user != stylo.session.user) {
				stylo.msgprint({
					message: __(
						"You've logged in as another user from another tab. Refresh this page to continue using system."
					),
					title: __("User Changed"),
					primary_action: {
						label: __("Refresh"),
						action: () => {
							window.location.reload();
						},
					},
				});
				return;
			}

			if (csrf_token) {
				// If user re-logged in then their other tabs won't be usable without this update.
				stylo.csrf_token = csrf_token;
			}
		});
	}

	setup_moment() {
		moment.updateLocale("en", {
			week: {
				dow: stylo.datetime.get_first_day_of_the_week_index(),
			},
		});
		moment.locale("en");
		moment.user_utc_offset = moment().utcOffset();
		if (stylo.boot.timezone_info) {
			moment.tz.add(stylo.boot.timezone_info);
		}
	}
};

stylo.get_module = function (m, default_module) {
	var module = stylo.modules[m] || default_module;
	if (!module) {
		return;
	}

	if (module._setup) {
		return module;
	}

	if (!module.label) {
		module.label = m;
	}

	if (!module._label) {
		module._label = __(module.label);
	}

	module._setup = true;

	return module;
};
