# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class PatchLog(Document):
	pass


def before_migrate():
	stylo.reload_doc("core", "doctype", "patch_log")
