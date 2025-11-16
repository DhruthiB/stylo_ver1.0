# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo

sitemap = 1


def get_context(context):
	context.doc = stylo.get_cached_doc("About Us Settings")

	return context
