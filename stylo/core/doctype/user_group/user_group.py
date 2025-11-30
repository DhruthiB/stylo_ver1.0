# Copyright (c) 2021, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo

# import stylo
from stylo.model.document import Document


class UserGroup(Document):
	def after_insert(self):
		stylo.cache().delete_key("user_groups")

	def on_trash(self):
		stylo.cache().delete_key("user_groups")
