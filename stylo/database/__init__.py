# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# Database Module
# --------------------

from stylo.database.database import savepoint


def setup_database(force, source_sql=None, verbose=None, no_mariadb_socket=False):
	import stylo

	if stylo.conf.db_type == "postgres":
		import stylo.database.postgres.setup_db

		return stylo.database.postgres.setup_db.setup_database(force, source_sql, verbose)
	else:
		import stylo.database.mariadb.setup_db

		return stylo.database.mariadb.setup_db.setup_database(
			force, source_sql, verbose, no_mariadb_socket=no_mariadb_socket
		)


def drop_user_and_database(db_name, root_login=None, root_password=None):
	import stylo

	if stylo.conf.db_type == "postgres":
		import stylo.database.postgres.setup_db

		return stylo.database.postgres.setup_db.drop_user_and_database(db_name, root_login, root_password)
	else:
		import stylo.database.mariadb.setup_db

		return stylo.database.mariadb.setup_db.drop_user_and_database(db_name, root_login, root_password)


def get_db(host=None, user=None, password=None, port=None):
	import stylo

	if stylo.conf.db_type == "postgres":
		import stylo.database.postgres.database

		return stylo.database.postgres.database.PostgresDatabase(host, user, password, port=port)
	else:
		import stylo.database.mariadb.database

		return stylo.database.mariadb.database.MariaDBDatabase(host, user, password, port=port)


def setup_help_database(help_db_name):
	import stylo

	if stylo.conf.db_type == "postgres":
		import stylo.database.postgres.setup_db

		return stylo.database.postgres.setup_db.setup_help_database(help_db_name)
	else:
		import stylo.database.mariadb.setup_db

		return stylo.database.mariadb.setup_db.setup_help_database(help_db_name)
