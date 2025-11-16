import stylo


def execute():
	doctype = "Integration Request"

	if not stylo.db.has_column(doctype, "integration_type"):
		return

	stylo.db.set_value(
		doctype,
		{"integration_type": "Remote", "integration_request_service": ("!=", "PayPal")},
		"is_remote_request",
		1,
	)
	stylo.db.set_value(
		doctype,
		{"integration_type": "Subscription Notification"},
		"request_description",
		"Subscription Notification",
	)
