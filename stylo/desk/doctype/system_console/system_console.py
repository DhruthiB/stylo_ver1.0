# Copyright (c) 2020, Stylo Technologies and contributors
# License: MIT. See LICENSE

import json

import stylo
from stylo.model.document import Document
from stylo.utils.safe_exec import read_sql, safe_exec


class SystemConsole(Document):
	def run(self):
		stylo.only_for("System Manager")
		try:
			stylo.local.debug_log = []
			if self.type == "Python":
				safe_exec(self.console)
				self.output = "\n".join(stylo.debug_log)
			elif self.type == "SQL":
				self.output = stylo.as_json(read_sql(self.console, as_dict=1))
		except Exception:
			self.commit = False
			self.output = stylo.get_traceback()

		if self.commit:
			stylo.db.commit()
		else:
			stylo.db.rollback()

		stylo.get_doc(dict(doctype="Console Log", script=self.console)).insert()
		stylo.db.commit()


@stylo.whitelist(methods=["POST"])
def execute_code(doc):
	console = stylo.get_doc(json.loads(doc))
	console.run()
	return console.as_dict()


@stylo.whitelist()
def show_processlist():
	stylo.only_for("System Manager")

	return stylo.db.multisql(
		{
			"postgres": """
			SELECT pid AS "Id",
				query_start AS "Time",
				state AS "State",
				query AS "Info",
				wait_event AS "Progress"
			FROM pg_stat_activity""",
			"mariadb": "show full processlist",
		},
		as_dict=True,
	)
