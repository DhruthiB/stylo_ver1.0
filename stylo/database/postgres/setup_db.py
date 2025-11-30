import os

import stylo


def setup_database(force, source_sql=None, verbose=False):
	root_conn = get_root_connection(stylo.flags.root_login, stylo.flags.root_password)
	root_conn.commit()
	root_conn.sql("end")
	root_conn.sql(f"DROP DATABASE IF EXISTS `{stylo.conf.db_name}`")
	root_conn.sql(f"DROP USER IF EXISTS {stylo.conf.db_name}")
	root_conn.sql(f"CREATE DATABASE `{stylo.conf.db_name}`")
	root_conn.sql(f"CREATE user {stylo.conf.db_name} password '{stylo.conf.db_password}'")
	root_conn.sql(f"GRANT ALL PRIVILEGES ON DATABASE `{stylo.conf.db_name}` TO {stylo.conf.db_name}")
	root_conn.close()

	bootstrap_database(stylo.conf.db_name, verbose, source_sql=source_sql)
	stylo.connect()


def bootstrap_database(db_name, verbose, source_sql=None):
	stylo.connect(db_name=db_name)
	import_db_from_sql(source_sql, verbose)
	stylo.connect(db_name=db_name)

	if "tabDefaultValue" not in stylo.db.get_tables():
		import sys

		from click import secho

		secho(
			"Table 'tabDefaultValue' missing in the restored site. "
			"This happens when the backup fails to restore. Please check that the file is valid\n"
			"Do go through the above output to check the exact error message from MariaDB",
			fg="red",
		)
		sys.exit(1)


def import_db_from_sql(source_sql=None, verbose=False):
	from shutil import which
	from subprocess import PIPE, run

	# we can't pass psql password in arguments in postgresql as mysql. So
	# set password connection parameter in environment variable
	subprocess_env = os.environ.copy()
	subprocess_env["PGPASSWORD"] = str(stylo.conf.db_password)

	# bootstrap db
	if not source_sql:
		source_sql = os.path.join(os.path.dirname(__file__), "framework_postgres.sql")

	pv = which("pv")

	_command = (
		f"psql {stylo.conf.db_name} "
		f"-h {stylo.conf.db_host or 'localhost'} -p {stylo.conf.db_port or '5432'!s} "
		f"-U {stylo.conf.db_name}"
	)

	if pv:
		command = f"{pv} {source_sql} | " + _command
	else:
		command = _command + f" -f {source_sql}"

	print("Restoring Database file...")
	if verbose:
		print(command)

	restore_proc = run(command, env=subprocess_env, shell=True, stdout=PIPE)

	if verbose:
		print(f"\nSTDOUT by psql:\n{restore_proc.stdout.decode()}\nImported from Database File: {source_sql}")


def setup_help_database(help_db_name):
	root_conn = get_root_connection(stylo.flags.root_login, stylo.flags.root_password)
	root_conn.sql(f"DROP DATABASE IF EXISTS `{help_db_name}`")
	root_conn.sql(f"DROP USER IF EXISTS {help_db_name}")
	root_conn.sql(f"CREATE DATABASE `{help_db_name}`")
	root_conn.sql(f"CREATE user {help_db_name} password '{help_db_name}'")
	root_conn.sql(f"GRANT ALL PRIVILEGES ON DATABASE `{help_db_name}` TO {help_db_name}")


def get_root_connection(root_login=None, root_password=None):
	if not stylo.local.flags.root_connection:
		if not root_login:
			root_login = stylo.conf.get("root_login") or None

		if not root_login:
			root_login = input("Enter postgres super user: ")

		if not root_password:
			root_password = stylo.conf.get("root_password") or None

		if not root_password:
			from getpass import getpass

			root_password = getpass("Postgres super user password: ")

		stylo.local.flags.root_connection = stylo.database.get_db(user=root_login, password=root_password)

	return stylo.local.flags.root_connection


def drop_user_and_database(db_name, root_login, root_password):
	root_conn = get_root_connection(
		stylo.flags.root_login or root_login, stylo.flags.root_password or root_password
	)
	root_conn.commit()
	root_conn.sql(
		"SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = %s",
		(db_name,),
	)
	root_conn.sql("end")
	root_conn.sql(f"DROP DATABASE IF EXISTS {db_name}")
	root_conn.sql(f"DROP USER IF EXISTS {db_name}")
