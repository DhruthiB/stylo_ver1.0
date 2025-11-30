# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class WebsiteScript(Document):
	def on_update(self):
		"""clear cache"""
		stylo.clear_cache(user="Guest")

		from stylo.website.utils import clear_cache

		clear_cache()
