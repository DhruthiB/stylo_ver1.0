# Copyright (c) 2018, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo import _
from stylo.model.document import Document
from stylo.utils import cint


class PrintSettings(Document):
	def validate(self):
		if self.pdf_page_size == "Custom" and not (self.pdf_page_height and self.pdf_page_width):
			stylo.throw(_("Page height and width cannot be zero"))

	def on_update(self):
		stylo.clear_cache()


@stylo.whitelist()
def is_print_server_enabled():
	if not hasattr(stylo.local, "enable_print_server"):
		stylo.local.enable_print_server = cint(
			stylo.db.get_single_value("Print Settings", "enable_print_server")
		)

	return stylo.local.enable_print_server
