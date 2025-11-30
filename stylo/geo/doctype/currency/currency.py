# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class Currency(Document):
	def validate(self):
		if not stylo.flags.in_install_app:
			stylo.clear_cache()
