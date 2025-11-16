# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.model.document import Document


class ClientScript(Document):
	def on_update(self):
		stylo.clear_cache(doctype=self.dt)

	def on_trash(self):
		stylo.clear_cache(doctype=self.dt)
