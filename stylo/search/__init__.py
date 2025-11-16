# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo
from stylo.search.full_text_search import FullTextSearch
from stylo.search.sqlite_search import SQLiteSearch
from stylo.search.website_search import WebsiteSearch
from stylo.utils import cint


@stylo.whitelist(allow_guest=True)
def web_search(query, scope=None, limit=20):
	limit = cint(limit)
	ws = WebsiteSearch(index_name="web_routes")
	return ws.search(query, scope, limit)
