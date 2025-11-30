# Copyright (c) 2022, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.deferred_insert import deferred_insert as _deferred_insert
from stylo.model.document import Document


class RouteHistory(Document):
	@staticmethod
	def clear_old_logs(days=30):
		from stylo.query_builder import Interval
		from stylo.query_builder.functions import Now

		table = stylo.qb.DocType("Route History")
		stylo.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@stylo.whitelist()
def deferred_insert(routes):
	routes = [
		{
			"user": stylo.session.user,
			"route": route.get("route"),
			"creation": route.get("creation"),
		}
		for route in stylo.parse_json(routes)
	]

	_deferred_insert("Route History", routes)


@stylo.whitelist()
def frequently_visited_links():
	return stylo.get_all(
		"Route History",
		fields=["route", "count(name) as count"],
		filters={"user": stylo.session.user},
		group_by="route",
		order_by="count desc",
		limit=5,
	)
