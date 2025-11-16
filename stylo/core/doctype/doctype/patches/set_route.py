import stylo
from stylo.desk.utils import slug


def execute():
	for doctype in stylo.get_all("DocType", ["name", "route"], dict(istable=0)):
		if not doctype.route:
			stylo.db.set_value("DocType", doctype.name, "route", slug(doctype.name), update_modified=False)
