// Copyright (c) 2024, Stylo Technologies and contributors
// For license information, please see license.txt

stylo.ui.form.on("Role Replication", {
	refresh(frm) {
		frm.disable_save();
		frm.page.set_primary_action(__("Replicate"), ($btn) => {
			$btn.text(__("Replicating..."));
			stylo.run_serially([
				() => stylo.dom.freeze("Replicating..."),
				() => frm.call("replicate_role"),
				() => stylo.dom.unfreeze(),
				() => stylo.msgprint(__("Replication completed.")),
				() => $btn.text(__("Replicate")),
			]);
		});
	},
});
