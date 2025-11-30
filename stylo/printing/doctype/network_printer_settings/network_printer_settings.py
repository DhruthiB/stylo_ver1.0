# Copyright (c) 2021, Stylo Technologies and contributors
# For license information, please see license.txt

import stylo
from stylo import _
from stylo.model.document import Document


class NetworkPrinterSettings(Document):
	@stylo.whitelist()
	def get_printers_list(self, ip="localhost", port=631):
		printer_list = []
		try:
			import cups
		except ImportError:
			stylo.throw(
				_(
					"""This feature can not be used as dependencies are missing.
				Please contact your system manager to enable this by installing pycups!"""
				)
			)
			return
		try:
			cups.setServer(self.server_ip)
			cups.setPort(self.port)
			conn = cups.Connection()
			printers = conn.getPrinters()
			for printer_id, printer in printers.items():
				printer_list.append({"value": printer_id, "label": printer["printer-make-and-model"]})

		except RuntimeError:
			stylo.throw(_("Failed to connect to server"))
		except stylo.ValidationError:
			stylo.throw(_("Failed to connect to server"))
		return printer_list


@stylo.whitelist()
def get_network_printer_settings():
	return stylo.db.get_list("Network Printer Settings", pluck="name")
