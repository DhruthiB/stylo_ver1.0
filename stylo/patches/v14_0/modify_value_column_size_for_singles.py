import stylo


def execute():
	if stylo.db.db_type == "mariadb":
		stylo.db.sql_ddl("alter table `tabSingles` modify column `value` longtext")
