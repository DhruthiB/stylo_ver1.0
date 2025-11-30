# Copyright (c) 2023, Stylo Technologies and contributors
# For license information, please see license.txt

import stylo
from stylo.model.document import Document
from stylo.query_builder.utils import DocType


class CustomHTMLBlock(Document):
	pass


@stylo.whitelist()
def get_custom_blocks_for_user(doctype, txt, searchfield, start, page_len, filters):
	# return logged in users private blocks and all public blocks
	customHTMLBlock = DocType("Custom HTML Block")

	condition_query = stylo.qb.get_query(customHTMLBlock)

	return (
		condition_query.select(customHTMLBlock.name).where(
			(customHTMLBlock.private == 0)
			| ((customHTMLBlock.owner == stylo.session.user) & (customHTMLBlock.private == 1))
		)
	).run()
