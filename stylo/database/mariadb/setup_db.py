import os

import click

import stylo
from stylo.database.db_manager import DbManager


def get_mariadb_variables():
	return stylo._dict(stylo.db.sql("show variables"))


def get_mariadb_version(version_string: str = ""):
	# MariaDB classifies their versions as Major (1st and 2nd number), and Minor (3rd number)
	# Example: Version 10.3.13 is Major Version = 10.3, Minor Version = 13
	version_string = version_string or get_mariadb_variables().get("version")
	version = version_string.split("-")[0]
	return version.rsplit(".", 1)


def setup_database(force, source_sql, verbose, no_mariadb_socket=False):
	stylo.local.session = stylo._dict({"user": "Administrator"})

	db_name = stylo.local.conf.db_name
	root_conn = get_root_connection(stylo.flags.root_login, stylo.flags.root_password)
	dbman = DbManager(root_conn)
	dbman_kwargs = {}
	if no_mariadb_socket:
		dbman_kwargs["host"] = "%"

	if force or (db_name not in dbman.get_database_list()):
		dbman.delete_user(db_name, **dbman_kwargs)
		dbman.drop_database(db_name)
	else:
		raise Exception(f"Database {db_name} already exists")

	dbman.create_user(db_name, stylo.conf.db_password, **dbman_kwargs)
	if verbose:
		print("Created user %s" % db_name)

	dbman.create_database(db_name)
	if verbose:
		print("Created database %s" % db_name)

	dbman.grant_all_privileges(db_name, db_name, **dbman_kwargs)
	dbman.flush_privileges()
	if verbose:
		print(f"Granted privileges to user {db_name} and database {db_name}")

	# close root connection
	root_conn.close()

	bootstrap_database(db_name, verbose, source_sql)


def setup_help_database(help_db_name):
	dbman = DbManager(get_root_connection(stylo.flags.root_login, stylo.flags.root_password))
	dbman.drop_database(help_db_name)

	# make database
	if help_db_name not in dbman.get_database_list():
		try:
			dbman.create_user(help_db_name, help_db_name)
		except Exception as e:
			# user already exists
			if e.args[0] != 1396:
				raise
		dbman.create_database(help_db_name)
		dbman.grant_all_privileges(help_db_name, help_db_name)
		dbman.flush_privileges()


def drop_user_and_database(db_name, root_login, root_password):
	stylo.local.db = get_root_connection(root_login, root_password)
	dbman = DbManager(stylo.local.db)
	dbman.drop_database(db_name)
	dbman.delete_user(db_name, host="%")
	dbman.delete_user(db_name)


def bootstrap_database(db_name, verbose, source_sql=None):
	import sys

	stylo.connect(db_name=db_name)
	check_compatible_versions()

	import_db_from_sql(source_sql, verbose)

	stylo.connect(db_name=db_name)
	if "tabDefaultValue" not in stylo.db.get_tables(cached=False):
		from click import secho

		secho(
			"Table 'tabDefaultValue' missing in the restored site. "
			"This happens when the backup fails to restore. Please check that the file is valid\n"
			"Do go through the above output to check the exact error message from MariaDB",
			fg="red",
		)
		sys.exit(1)


def import_db_from_sql(source_sql=None, verbose=False):
	if verbose:
		print("Starting database import...")
	db_name = stylo.conf.db_name
	if not source_sql:
		source_sql = os.path.join(os.path.dirname(__file__), "framework_mariadb.sql")
	DbManager(stylo.local.db).restore_database(db_name, source_sql, db_name, stylo.conf.db_password)
	if verbose:
		print("Imported from database %s" % source_sql)


def check_compatible_versions():
	try:
		version = get_mariadb_version()
		version_tuple = tuple(int(v) for v in version[0].split("."))

		if version_tuple < (10, 3):
			click.secho(
				f"Warning: MariaDB version {version} is less than 10.3 which is not supported by Stylo",
				fg="yellow",
			)
		elif version_tuple >= (10, 9):
			click.secho(
				f"Warning: MariaDB version {version} is more than 10.8 which is not yet tested with Stylo Framework.",
				fg="yellow",
			)
	except Exception:
		click.secho(
			"MariaDB version compatibility checks failed, make sure you're running a supported version.",
			fg="yellow",
		)


def get_root_connection(root_login, root_password):
	import getpass

	if not stylo.local.flags.root_connection:
		if not root_login:
			root_login = "root"

		if not root_password:
			root_password = stylo.conf.get("root_password") or None

		if not root_password:
			root_password = getpass.getpass("MySQL root password: ")

		stylo.local.flags.root_connection = stylo.database.get_db(user=root_login, password=root_password)

	return stylo.local.flags.root_connection
