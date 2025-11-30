# Copyright (c) 2021, Stylo Technologies and contributors
# For license information, please see license.txt

import stylo
from stylo import _
from stylo.model.document import Document


class PrintFormatFieldTemplate(Document):
	def validate(self):
		if self.standard and not (stylo.conf.developer_mode or stylo.flags.in_patch):
			stylo.throw(_("Enable developer mode to create a standard Print Template"))

	def before_insert(self):
		self.validate_duplicate()

	def on_update(self):
		self.validate_duplicate()
		self.export_doc()

	def validate_duplicate(self):
		if not self.standard:
			return
		if not self.field:
			return

		filters = {"document_type": self.document_type, "field": self.field}
		if not self.is_new():
			filters.update({"name": ("!=", self.name)})
		result = stylo.get_all("Print Format Field Template", filters=filters, limit=1)
		if result:
			stylo.throw(
				_("A template already exists for field {0} of {1}").format(
					stylo.bold(self.field), stylo.bold(self.document_type)
				),
				stylo.DuplicateEntryError,
				title=_("Duplicate Entry"),
			)

	def export_doc(self):
		from stylo.modules.utils import export_module_json

		export_module_json(self, self.standard, self.module)
