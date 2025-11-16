"""
Run this after updating country_info.json and or
"""
import stylo


def execute():
	for col in ("field", "doctype"):
		stylo.db.sql_ddl(f"alter table `tabSingles` modify column `{col}` varchar(255)")
