import stylo


def execute():
	stylo.reload_doc("core", "doctype", "user")
	stylo.db.sql(
		"""
		UPDATE `tabUser`
		SET `home_settings` = ''
		WHERE `user_type` = 'System User'
	"""
	)
