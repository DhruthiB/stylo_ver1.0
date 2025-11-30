# Copyright (c) 2017, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class PrintStyle(Document):
	def validate(self):
		if (
			self.standard == 1
			and not stylo.local.conf.get("developer_mode")
			and not (stylo.flags.in_import or stylo.flags.in_test)
		):
			stylo.throw(stylo._("Standard Print Style cannot be changed. Please duplicate to edit."))

	def on_update(self):
		self.export_doc()

	def export_doc(self):
		# export
		from stylo.modules.utils import export_module_json

		export_module_json(self, self.standard == 1, "Printing")
