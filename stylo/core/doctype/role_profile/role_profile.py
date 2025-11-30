# Copyright (c) 2017, Stylo Technologies and contributors
# License: MIT. See LICENSE

from collections import defaultdict

import stylo
from stylo.model.document import Document


class RoleProfile(Document):
	def autoname(self):
		"""set name as Role Profile name"""
		self.name = self.role_profile

	def on_update(self):
		"""Changes in role_profile reflected across all its user"""
		has_role = stylo.qb.DocType("Has Role")
		user = stylo.qb.DocType("User")

		all_current_roles = (
			stylo.qb.from_(user)
			.join(has_role)
			.on(user.name == has_role.parent)
			.where(user.role_profile_name == self.name)
			.select(user.name, has_role.role)
		).run()

		user_roles = defaultdict(set)
		for user, role in all_current_roles:
			user_roles[user].add(role)

		role_profile_roles = {role.role for role in self.roles}
		for user, roles in user_roles.items():
			if roles != role_profile_roles:
				user = stylo.get_doc("User", user)
				user.roles = []
				user.add_roles(*role_profile_roles)
