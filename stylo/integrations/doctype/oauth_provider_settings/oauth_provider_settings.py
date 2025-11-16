# Copyright (c) 2015, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo import _
from stylo.model.document import Document


class OAuthProviderSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		skip_authorization: DF.Literal["Force", "Auto"]
	# end: auto-generated types

	pass
