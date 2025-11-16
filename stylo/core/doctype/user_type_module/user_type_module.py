# Copyright (c) 2021, Stylo Technologies and contributors
# License: MIT. See LICENSE

# import stylo
from stylo.model.document import Document


class UserTypeModule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		module: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	pass
