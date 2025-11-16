import stylo


def execute():
	days = stylo.db.get_single_value("Website Settings", "auto_account_deletion")
	stylo.db.set_single_value("Website Settings", "auto_account_deletion", days * 24)
