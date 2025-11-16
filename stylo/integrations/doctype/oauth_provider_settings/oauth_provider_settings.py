# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo import _
from stylo.model.document import Document


class OAuthProviderSettings(Document):
	pass


def get_oauth_settings():
	"""Returns oauth settings"""
	out = stylo._dict(
		{"skip_authorization": stylo.db.get_single_value("OAuth Provider Settings", "skip_authorization")}
	)

	return out
