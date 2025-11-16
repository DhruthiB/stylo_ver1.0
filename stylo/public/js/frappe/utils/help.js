// Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

stylo.provide("stylo.help");

stylo.help.youtube_id = {};

stylo.help.has_help = function (doctype) {
	return stylo.help.youtube_id[doctype];
};

stylo.help.show = function (doctype) {
	if (stylo.help.youtube_id[doctype]) {
		stylo.help.show_video(stylo.help.youtube_id[doctype]);
	}
};

stylo.help.show_video = function (youtube_id, title) {
	if (stylo.utils.is_url(youtube_id)) {
		const expression =
			'(?:youtube.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu.be/)([^"&?\\s]{11})';
		youtube_id = youtube_id.match(expression)[1];
	}

	// (stylo.help_feedback_link || "")
	let dialog = new stylo.ui.Dialog({
		title: title || __("Help"),
		size: "large",
	});

	let video = $(
		`<div class="video-player" data-plyr-provider="youtube" data-plyr-embed-id="${youtube_id}"></div>`
	);
	video.appendTo(dialog.body);

	dialog.show();
	dialog.$wrapper.addClass("video-modal");

	let plyr;
	stylo.utils.load_video_player().then(() => {
		plyr = new stylo.Plyr(video[0], {
			hideControls: true,
			resetOnEnd: true,
		});
	});

	dialog.onhide = () => {
		plyr?.destroy();
	};
};

$("body").on("click", "a.help-link", function () {
	var doctype = $(this).attr("data-doctype");
	doctype && stylo.help.show(doctype);
});
