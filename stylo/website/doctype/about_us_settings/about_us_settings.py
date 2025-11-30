# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class AboutUsSettings(Document):
	def on_update(self):
		from stylo.website.utils import clear_cache

		clear_cache("about")


def get_args():
	obj = stylo.get_doc("About Us Settings")
	return {"obj": obj}
