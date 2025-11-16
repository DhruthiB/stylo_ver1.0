# Copyright (c) 2022, Stylo Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import stylo


def execute():
	doctypes = stylo.get_all("DocType", {"module": "Data Migration", "custom": 0}, pluck="name")
	for doctype in doctypes:
		stylo.delete_doc("DocType", doctype, ignore_missing=True)

	stylo.delete_doc("Module Def", "Data Migration", ignore_missing=True, force=True)
