# Copyright (c) 2020, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo.model.document import Document


class ConsoleLog(Document):
	def after_delete(self):
		# because on_trash can be bypassed
		stylo.throw(stylo._("Console Logs can not be deleted"))
