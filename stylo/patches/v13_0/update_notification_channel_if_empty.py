# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo


def execute():
	stylo.reload_doc("Email", "doctype", "Notification")

	notifications = stylo.get_all("Notification", {"is_standard": 1}, {"name", "channel"})
	for notification in notifications:
		if not notification.channel:
			stylo.db.set_value("Notification", notification.name, "channel", "Email", update_modified=False)
			stylo.db.commit()
