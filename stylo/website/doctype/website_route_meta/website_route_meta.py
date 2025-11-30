# Copyright (c) 2019, Stylo Technologies and contributors
# License: MIT. See LICENSE

from stylo.model.document import Document


class WebsiteRouteMeta(Document):
	def autoname(self):
		if self.name and self.name.startswith("/"):
			self.name = self.name[1:]
