// Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

if (stylo.require) {
	stylo.require("file_uploader.bundle.js");
} else {
	stylo.ready(function () {
		stylo.require("file_uploader.bundle.js");
	});
}
