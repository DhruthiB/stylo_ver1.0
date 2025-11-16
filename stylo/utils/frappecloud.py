import stylo

FRAPPE_CLOUD_DOMAINS = ("stylo.cloud", "erpnext.com", "stylohr.com", "stylo.dev")


def on_stylocloud() -> bool:
	"""Returns true if running on Stylo Cloud.


	Useful for modifying few features for better UX."""
	return stylo.local.site.endswith(FRAPPE_CLOUD_DOMAINS)
