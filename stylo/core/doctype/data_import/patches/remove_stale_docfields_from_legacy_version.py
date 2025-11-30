import stylo


def execute():
	"""Remove stale docfields from legacy version"""
	stylo.db.delete("DocField", {"options": "Data Import", "parent": "Data Import Legacy"})
