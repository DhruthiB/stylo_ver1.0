import stylo
from stylo.model.utils.rename_field import rename_field


def execute():
	if not stylo.db.table_exists("Dashboard Chart"):
		return

	stylo.reload_doc("desk", "doctype", "dashboard_chart")

	if stylo.db.has_column("Dashboard Chart", "is_custom"):
		rename_field("Dashboard Chart", "is_custom", "use_report_chart")
