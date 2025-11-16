import json

import stylo


@stylo.whitelist()
def get_onboarding_status():
	onboarding_status = stylo.db.get_value("User", stylo.session.user, "onboarding_status")
	return stylo.parse_json(onboarding_status) if onboarding_status else {}


@stylo.whitelist()
def update_user_onboarding_status(steps: str, appName: str):
	steps = json.loads(steps)

	# get the current onboarding status
	onboarding_status = stylo.db.get_value("User", stylo.session.user, "onboarding_status")
	onboarding_status = stylo.parse_json(onboarding_status)

	# update the onboarding status
	onboarding_status[appName + "_onboarding_status"] = steps

	stylo.db.set_value(
		"User", stylo.session.user, "onboarding_status", json.dumps(onboarding_status), update_modified=False
	)
