# Copyright (c) 2020, Stylo Technologies and contributors
# License: MIT. See LICENSE

import json

import stylo

# import stylo
from stylo.model.document import Document


class DashboardSettings(Document):
	pass


@stylo.whitelist()
def create_dashboard_settings(user):
	if not stylo.db.exists("Dashboard Settings", user):
		doc = stylo.new_doc("Dashboard Settings")
		doc.name = user
		doc.insert(ignore_permissions=True)
		stylo.db.commit()
		return doc


def get_permission_query_conditions(user):
	if not user:
		user = stylo.session.user

	return f"""(`tabDashboard Settings`.name = {stylo.db.escape(user)})"""


@stylo.whitelist()
def save_chart_config(reset, config, chart_name):
	reset = stylo.parse_json(reset)
	doc = stylo.get_doc("Dashboard Settings", stylo.session.user)
	chart_config = stylo.parse_json(doc.chart_config) or {}

	if reset:
		chart_config[chart_name] = {}
	else:
		config = stylo.parse_json(config)
		if chart_name not in chart_config:
			chart_config[chart_name] = {}
		chart_config[chart_name].update(config)

	stylo.db.set_value("Dashboard Settings", stylo.session.user, "chart_config", json.dumps(chart_config))
