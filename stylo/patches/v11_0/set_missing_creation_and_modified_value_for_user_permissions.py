import stylo


def execute():
	stylo.db.sql(
		"""UPDATE `tabUser Permission`
		SET `modified`=NOW(), `creation`=NOW()
		WHERE `creation` IS NULL"""
	)
