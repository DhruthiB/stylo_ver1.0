import json

import stylo


def execute():
	if stylo.db.exists("Social Login Key", "github"):
		stylo.db.set_value(
			"Social Login Key", "github", "auth_url_data", json.dumps({"scope": "user:email"})
		)
