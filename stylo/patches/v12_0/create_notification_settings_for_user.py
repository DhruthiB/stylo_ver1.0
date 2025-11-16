import stylo
from stylo.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
)


def execute():
	stylo.reload_doc("desk", "doctype", "notification_settings")
	stylo.reload_doc("desk", "doctype", "notification_subscribed_document")

	users = stylo.get_all("User", fields=["name"])
	for user in users:
		create_notification_settings(user.name)
