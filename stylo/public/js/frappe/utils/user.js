stylo.user_info = function (uid) {
	if (!uid) uid = stylo.session.user;

	if (!(stylo.boot.user_info && stylo.boot.user_info[uid])) {
		var user_info = { fullname: uid || "Unknown" };
	} else {
		var user_info = stylo.boot.user_info[uid];
	}

	user_info.abbr = stylo.get_abbr(user_info.fullname);
	user_info.color = stylo.get_palette(user_info.fullname);

	return user_info;
};

stylo.update_user_info = function (user_info) {
	for (let user in user_info) {
		if (stylo.boot.user_info[user]) {
			Object.assign(stylo.boot.user_info[user], user_info[user]);
		} else {
			stylo.boot.user_info[user] = user_info[user];
		}
	}
};

stylo.provide("stylo.user");

$.extend(stylo.user, {
	name: "Guest",
	full_name: function (uid) {
		return uid === stylo.session.user
			? __(
					"You",
					null,
					"Name of the current user. For example: You edited this 5 hours ago."
			  )
			: stylo.user_info(uid).fullname;
	},
	image: function (uid) {
		return stylo.user_info(uid).image;
	},
	abbr: function (uid) {
		return stylo.user_info(uid).abbr;
	},
	has_role: function (rl) {
		if (typeof rl == "string") rl = [rl];
		for (var i in rl) {
			if ((stylo.boot ? stylo.boot.user.roles : ["Guest"]).indexOf(rl[i]) != -1)
				return true;
		}
	},
	get_desktop_items: function () {
		// hide based on permission
		var modules_list = $.map(stylo.boot.allowed_modules, function (icon) {
			var m = icon.module_name;
			var type = stylo.modules[m] && stylo.modules[m].type;

			if (stylo.boot.user.allow_modules.indexOf(m) === -1) return null;

			var ret = null;
			if (type === "module") {
				if (stylo.boot.user.allow_modules.indexOf(m) != -1 || stylo.modules[m].is_help)
					ret = m;
			} else if (type === "page") {
				if (stylo.boot.allowed_pages.indexOf(stylo.modules[m].link) != -1) ret = m;
			} else if (type === "list") {
				if (stylo.model.can_read(stylo.modules[m]._doctype)) ret = m;
			} else if (type === "view") {
				ret = m;
			} else if (type === "setup") {
				if (
					stylo.user.has_role("System Manager") ||
					stylo.user.has_role("Administrator")
				)
					ret = m;
			} else {
				ret = m;
			}

			return ret;
		});

		return modules_list;
	},

	is_report_manager: function () {
		return stylo.user.has_role(["Administrator", "System Manager", "Report Manager"]);
	},

	get_formatted_email: function (email) {
		var fullname = stylo.user.full_name(email);

		if (!fullname) {
			return email;
		} else {
			// to quote or to not
			var quote = "";

			// only if these special characters are found
			// why? To make the output same as that in python!
			if (fullname.search(/[\[\]\\()<>@,:;".]/) !== -1) {
				quote = '"';
			}

			return repl("%(quote)s%(fullname)s%(quote)s <%(email)s>", {
				fullname: fullname,
				email: email,
				quote: quote,
			});
		}
	},

	get_emails: () => {
		return Object.keys(stylo.boot.user_info).map((key) => stylo.boot.user_info[key].email);
	},

	/* Normally stylo.user is an object
	 * having properties and methods.
	 * But in the following case
	 *
	 * if (stylo.user === 'Administrator')
	 *
	 * stylo.user will cast to a string
	 * returning stylo.user.name
	 */
	toString: function () {
		return this.name;
	},
});

stylo.session_alive = true;
$(document).bind("mousemove", function () {
	if (stylo.session_alive === false) {
		$(document).trigger("session_alive");
	}
	stylo.session_alive = true;
	if (stylo.session_alive_timeout) clearTimeout(stylo.session_alive_timeout);
	stylo.session_alive_timeout = setTimeout("stylo.session_alive=false;", 30000);
});
