# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class HasRole(Document):
	def before_insert(self):
		if stylo.db.exists("Has Role", {"parent": self.parent, "role": self.role}):
			stylo.throw(stylo._("User '{0}' already has the role '{1}'").format(self.parent, self.role))
