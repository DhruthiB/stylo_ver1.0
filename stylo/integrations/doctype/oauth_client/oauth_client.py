# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo import _
from stylo.model.document import Document


class OAuthClient(Document):
	def validate(self):
		self.client_id = self.name
		if not self.client_secret:
			self.client_secret = stylo.generate_hash(length=10)
		self.validate_grant_and_response()
		self.add_default_role()

	def validate_grant_and_response(self):
		if (
			self.grant_type == "Authorization Code"
			and self.response_type != "Code"
			or self.grant_type == "Implicit"
			and self.response_type != "Token"
		):
			stylo.throw(
				_(
					"Combination of Grant Type (<code>{0}</code>) and Response Type (<code>{1}</code>) not allowed"
				).format(self.grant_type, self.response_type)
			)

	def add_default_role(self):
		if not self.allowed_roles:
			self.append("allowed_roles", {"role": "All"})

	def user_has_allowed_role(self) -> bool:
		"""Returns true if session user is allowed to use this client."""
		allowed_roles = {d.role for d in self.allowed_roles}
		return bool(allowed_roles & set(stylo.get_roles()))
