import stylo


def execute():
	stylo.db.change_column_type("__Auth", column="password", type="TEXT")
