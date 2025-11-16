stylo.provide("stylo.model");
stylo.provide("stylo.utils");

/**
 * Opens the Website Meta Tag form if it exists for {route}
 * or creates a new doc and opens the form
 */
stylo.utils.set_meta_tag = function (route) {
	stylo.db.exists("Website Route Meta", route).then((exists) => {
		if (exists) {
			stylo.set_route("Form", "Website Route Meta", route);
		} else {
			// new doc
			const doc = stylo.model.get_new_doc("Website Route Meta");
			doc.__newname = route;
			stylo.set_route("Form", doc.doctype, doc.name);
		}
	});
};
