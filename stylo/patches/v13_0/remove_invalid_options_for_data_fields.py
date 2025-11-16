# Copyright (c) 2022, Stylo and Contributors
# License: MIT. See LICENSE


import stylo
from stylo.model import data_field_options


def execute():
	custom_field = stylo.qb.DocType("Custom Field")
	(
		stylo.qb.update(custom_field)
		.set(custom_field.options, None)
		.where((custom_field.fieldtype == "Data") & (custom_field.options.notin(data_field_options)))
	).run()
