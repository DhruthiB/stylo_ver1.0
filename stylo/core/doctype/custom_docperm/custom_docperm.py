# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class CustomDocPerm(Document):
	def on_update(self):
		stylo.clear_cache(doctype=self.parent)
