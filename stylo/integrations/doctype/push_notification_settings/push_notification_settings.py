# Copyright (c) 2024, Stylo Technologies and contributors
# For license information, please see license.txt

import stylo
from stylo import _
from stylo.model.document import Document


class PushNotificationSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from stylo.types import DF

		api_key: DF.Data | None
		api_secret: DF.Password | None
		enable_push_notification_relay: DF.Check
	# end: auto-generated types

	def validate(self):
		self.validate_relay_server_setup()

	def validate_relay_server_setup(self):
		if self.enable_push_notification_relay and not stylo.conf.get("push_relay_server_url"):
			stylo.throw(
				_("The Push Relay Server URL key (`push_relay_server_url`) is missing in your site config"),
				title=_("Relay Server URL missing"),
			)
