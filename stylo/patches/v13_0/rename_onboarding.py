# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	if stylo.db.exists("DocType", "Onboarding"):
		stylo.rename_doc("DocType", "Onboarding", "Module Onboarding", ignore_if_exists=True)
