import stylo
from stylo.cache_manager import clear_defaults_cache


def execute():
	stylo.db.set_default(
		"suspend_email_queue",
		stylo.db.get_default("hold_queue", "Administrator") or 0,
		parent="__default",
	)

	stylo.db.delete("DefaultValue", {"defkey": "hold_queue"})
	clear_defaults_cache()
