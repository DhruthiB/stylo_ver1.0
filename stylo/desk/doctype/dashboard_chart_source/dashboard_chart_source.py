# Copyright (c) 2019, Stylo Technologies and contributors
# License: MIT. See LICENSE

import os

import stylo
from stylo.model.document import Document
from stylo.modules import get_module_path, scrub
from stylo.modules.export_file import export_to_files


@stylo.whitelist()
def get_config(name):
	doc = stylo.get_doc("Dashboard Chart Source", name)
	with open(
		os.path.join(
			get_module_path(doc.module), "dashboard_chart_source", scrub(doc.name), scrub(doc.name) + ".js"
		),
	) as f:
		return f.read()


class DashboardChartSource(Document):
	def on_update(self):
		export_to_files(record_list=[[self.doctype, self.name]], record_module=self.module, create_init=True)
