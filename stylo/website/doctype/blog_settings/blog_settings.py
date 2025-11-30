# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class BlogSettings(Document):
	def on_update(self):
		from stylo.website.utils import clear_cache

		clear_cache("blog")
		clear_cache("writers")


def get_like_limit():
	return stylo.db.get_single_value("Blog Settings", "like_limit") or 5


def get_comment_limit():
	return stylo.db.get_single_value("Blog Settings", "comment_limit") or 5
