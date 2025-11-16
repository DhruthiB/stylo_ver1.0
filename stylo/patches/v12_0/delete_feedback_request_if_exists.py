import stylo


def execute():
	stylo.db.delete("DocType", {"name": "Feedback Request"})
