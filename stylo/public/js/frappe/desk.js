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
		stylo.socketio.init();
		stylo.model.init();

		this.setup_stylo_vue();
		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.set_favicon();
		this.setup_analytics();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_energy_point_listeners();
		this.setup_copy_doc_listener();

		stylo.ui.keys.setup();

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

		// page container
		this.make_page_container();
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
		this.set_route();

		// trigger app startup
		$(document).trigger("startup");

		$(document).trigger("app_ready");

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

		this.show_notes();

		if (stylo.ui.startup_setup_dialog && !stylo.boot.setup_complete) {
			stylo.ui.startup_setup_dialog.pre_show();
			stylo.ui.startup_setup_dialog.show();
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
		});
	}

	setup_stylo_vue() {
		Vue.prototype.__ = window.__;
		Vue.prototype.stylo = window.stylo;
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
			stylo.user.name = stylo.boot.user.name;
			stylo.router.setup();
		} else {
			this.set_as_guest();
		}
	}

	setup_workspaces() {
		stylo.modules = {};
		stylo.workspaces = {};
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

		// Proxy for user globals
		Object.defineProperties(window, {
			user: {
				get: function () {
					console.warn(
						"Please use `stylo.session.user` instead of `user`. It will be deprecated soon."
					);
					return stylo.session.user;
				},
			},
			user_fullname: {
				get: function () {
					console.warn(
						"Please use `stylo.session.user_fullname` instead of `user_fullname`. It will be deprecated soon."
					);
					return stylo.session.user;
				},
			},
			user_email: {
				get: function () {
					console.warn(
						"Please use `stylo.session.user_email` instead of `user_email`. It will be deprecated soon."
					);
					return stylo.session.user_email;
				},
			},
			user_defaults: {
				get: function () {
					console.warn(
						"Please use `stylo.user_defaults` instead of `user_defaults`. It will be deprecated soon."
					);
					return stylo.user_defaults;
				},
			},
			roles: {
				get: function () {
					console.warn(
						"Please use `stylo.user_roles` instead of `roles`. It will be deprecated soon."
					);
					return stylo.user_roles;
				},
			},
			sys_defaults: {
				get: function () {
					console.warn(
						"Please use `stylo.sys_defaults` instead of `sys_defaults`. It will be deprecated soon."
					);
					return stylo.user_roles;
				},
			},
		});
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
		if (!stylo.app.session_expired_dialog) {
			var dialog = new stylo.ui.Dialog({
				title: __("Session Expired"),
				keep_open: true,
				fields: [
					{
						fieldtype: "Password",
						fieldname: "password",
						label: __("Please Enter Your Password to Continue"),
					},
				],
				onhide: () => {
					if (!dialog.logged_in) {
						stylo.app.redirect_to_login();
					}
				},
			});
			dialog.get_field("password").disable_password_checks();
			dialog.set_primary_action(__("Login"), () => {
				dialog.set_message(__("Authenticating..."));
				stylo.call({
					method: "login",
					args: {
						usr: stylo.session.user,
						pwd: dialog.get_values().password,
					},
					callback: (r) => {
						if (r.message === "Logged In") {
							dialog.logged_in = true;

							// revert backdrop
							$(".modal-backdrop").css({
								opacity: "",
								"background-color": "#334143",
							});
						}
						dialog.hide();
					},
					statusCode: () => {
						dialog.hide();
					},
				});
			});
			stylo.app.session_expired_dialog = dialog;
		}
		if (!stylo.app.session_expired_dialog.display) {
			stylo.app.session_expired_dialog.show();
			// add backdrop
			$(".modal-backdrop").css({
				opacity: 1,
				"background-color": "#4B4C9D",
			});
		}
	}
	redirect_to_login() {
		window.location.href = "/";
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
		if (stylo.boot.sysdefaults.disable_system_update_notification) return;

		stylo.call({
			method: "stylo.utils.change_log.show_update_popup",
		});
	}

	setup_analytics() {
		if (window.mixpanel) {
			window.mixpanel.identify(stylo.session.user);
			window.mixpanel.people.set({
				$first_name: stylo.boot.user.first_name,
				$last_name: stylo.boot.user.last_name,
				$created: stylo.boot.user.creation,
				$email: stylo.session.user,
			});
		}
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
					var d = stylo.msgprint({ message: note.content, title: note.title });
					d.keep_open = true;
					d.custom_onhide = function () {
						note.seen = true;

						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							stylo.call({
								method: "stylo.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name,
								},
							});
						}

						// next note
						me.show_notes();
					};
				}
			});
		}
	}

	setup_build_events() {
		if (stylo.boot.developer_mode) {
			stylo.require("build_events.bundle.js");
		}
	}

	setup_energy_point_listeners() {
		stylo.realtime.on("energy_point_alert", (message) => {
			stylo.show_alert(message);
		});
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
							stylo.set_route("Form", newdoc.doctype, newdoc.name);
							stylo.dom.unfreeze();
						});
						res && res.fail(stylo.dom.unfreeze);
					});
				}
			} catch (e) {
				//
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
