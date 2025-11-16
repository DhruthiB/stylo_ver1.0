import stylo


def execute():
	if "payments" in stylo.get_installed_apps():
		return

	for doctype in (
		"Payment Gateway",
		"Razorpay Settings",
		"Braintree Settings",
		"PayPal Settings",
		"Paytm Settings",
		"Stripe Settings",
	):
		stylo.delete_doc_if_exists("DocType", doctype, force=True)
