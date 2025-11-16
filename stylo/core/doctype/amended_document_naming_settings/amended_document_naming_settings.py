# Copyright (c) 2023, Stylo Technologies and contributors
# For license information, please see license.txt

# import stylo
from stylo.model.document import Document


class AmendedDocumentNamingSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		action: DF.Literal["Amend Counter", "Default Naming"]
		document_type: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	pass
