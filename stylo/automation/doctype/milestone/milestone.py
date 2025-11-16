# Copyright (c) 2019, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class Milestone(Document):
	pass


def on_doctype_update():
	stylo.db.add_index("Milestone", ["reference_type", "reference_name"])
