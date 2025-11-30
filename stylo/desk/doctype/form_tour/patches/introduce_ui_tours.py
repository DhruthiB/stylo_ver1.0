import json

import stylo


def execute():
	"""Handle introduction of UI tours"""
	completed = {}
	for tour in stylo.get_all("Form Tour", {"ui_tour": 1}, pluck="name"):
		completed[tour] = {"is_complete": True}

	User = stylo.qb.DocType("User")
	stylo.qb.update(User).set("onboarding_status", json.dumps(completed)).run()
