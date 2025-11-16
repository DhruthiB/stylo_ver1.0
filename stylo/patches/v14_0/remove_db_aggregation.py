import re

import stylo
from stylo.query_builder import DocType


def execute():
	"""Replace temporarily available Database Aggregate APIs on stylo (develop)

	APIs changed:
	        * stylo.db.max => stylo.qb.max
	        * stylo.db.min => stylo.qb.min
	        * stylo.db.sum => stylo.qb.sum
	        * stylo.db.avg => stylo.qb.avg
	"""
	ServerScript = DocType("Server Script")
	server_scripts = (
		stylo.qb.from_(ServerScript)
		.where(
			ServerScript.script.like("%stylo.db.max(%")
			| ServerScript.script.like("%stylo.db.min(%")
			| ServerScript.script.like("%stylo.db.sum(%")
			| ServerScript.script.like("%stylo.db.avg(%")
		)
		.select("name", "script")
		.run(as_dict=True)
	)

	for server_script in server_scripts:
		name, script = server_script["name"], server_script["script"]

		for agg in ["avg", "max", "min", "sum"]:
			script = re.sub(f"stylo.db.{agg}\\(", f"stylo.qb.{agg}(", script)

		stylo.db.update("Server Script", name, "script", script)
