# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	stylo.delete_doc("DocType", "Package Publish Tool", ignore_missing=True)
	stylo.delete_doc("DocType", "Package Document Type", ignore_missing=True)
	stylo.delete_doc("DocType", "Package Publish Target", ignore_missing=True)
