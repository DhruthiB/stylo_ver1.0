import stylo


def execute():
	if stylo.db.db_type == "mariadb":
		stylo.db.sql(
			"ALTER TABLE __UserSettings CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
		)
