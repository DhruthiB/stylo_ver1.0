# Copyright (c) 2024, Stylo Technologies and contributors
# For license information, please see license.txt

# import stylo
from stylo.model.document import Document


class OAuthClientRole(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		role: DF.Link | None
	# end: auto-generated types

	pass
