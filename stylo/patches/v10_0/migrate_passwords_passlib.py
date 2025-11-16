import stylo
from stylo.utils.password import LegacyPassword


def execute():
	all_auths = stylo.db.sql(
		"""SELECT `name`, `password`, `salt` FROM `__Auth`
		WHERE doctype='User' AND `fieldname`='password'""",
		as_dict=True,
	)

	for auth in all_auths:
		if auth.salt and auth.salt != "":
			pwd = LegacyPassword.hash(auth.password, salt=auth.salt.encode("UTF-8"))
			stylo.db.sql(
				"""UPDATE `__Auth` SET `password`=%(pwd)s, `salt`=NULL
				WHERE `doctype`='User' AND `fieldname`='password' AND `name`=%(user)s""",
				{"pwd": pwd, "user": auth.name},
			)

	stylo.reload_doctype("User")

	stylo.db.sql_ddl("""ALTER TABLE `__Auth` DROP COLUMN `salt`""")
