stylo.pages["user-profile"].on_page_load = function (wrapper) {
	stylo.require("user_profile_controller.bundle.js", () => {
		let user_profile = new stylo.ui.UserProfile(wrapper);
		user_profile.show();
	});
};
