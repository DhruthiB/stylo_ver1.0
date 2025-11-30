# Copyright (c) 2020, Stylo Technologies and contributors
# License: MIT. See LICENSE

import stylo
from stylo import _
from stylo.boot import get_allowed_report_names
from stylo.config import get_modules_from_all_apps_for_user
from stylo.model.document import Document
from stylo.model.naming import append_number_if_name_exists
from stylo.modules.export_file import export_to_files
from stylo.permissions import get_doctypes_with_read
from stylo.query_builder import Criterion
from stylo.query_builder.utils import DocType
from stylo.utils import flt


class NumberCard(Document):
	def autoname(self):
		if not self.name:
			self.name = self.label

		if stylo.db.exists("Number Card", self.name):
			self.name = append_number_if_name_exists("Number Card", self.name)

	def validate(self):
		if self.type == "Document Type":
			if not (self.document_type and self.function):
				stylo.throw(_("Document Type and Function are required to create a number card"))

			if self.function != "Count" and not self.aggregate_function_based_on:
				stylo.throw(_("Aggregate Field is required to create a number card"))

			if stylo.get_meta(self.document_type).istable and not self.parent_document_type:
				stylo.throw(_("Parent Document Type is required to create a number card"))

		elif self.type == "Report":
			if not (self.report_name and self.report_field and self.function):
				stylo.throw(_("Report Name, Report Field and Fucntion are required to create a number card"))

		elif self.type == "Custom":
			if not self.method:
				stylo.throw(_("Method is required to create a number card"))

	def on_update(self):
		if stylo.conf.developer_mode and self.is_standard:
			export_to_files(record_list=[["Number Card", self.name]], record_module=self.module)


def get_permission_query_conditions(user=None):
	# The user param is ignored because `get_allowed_report_names` and `get_doctypes_with_read` don't support it.
	if stylo.session.user == "Administrator":
		return

	if "System Manager" in stylo.get_roles():
		return

	allowed_reports = get_allowed_report_names()
	allowed_doctypes = get_doctypes_with_read()
	allowed_modules = [module.get("module_name") for module in get_modules_from_all_apps_for_user()]

	nc = stylo.qb.DocType("Number Card")
	conditions = (
		((nc.type == "Report") & nc.report_name.isin(allowed_reports))
		| ((nc.type == "Custom") & nc.document_type.isin(allowed_doctypes))
		| ((nc.type == "Document Type") & nc.document_type.isin(allowed_doctypes))
	) & (nc.module.isin(allowed_modules) | nc.module.isnull() | nc.module == "")

	return conditions.get_sql(quote_char="`")


def has_permission(doc, ptype, user):
	# The user param is ignored because `get_allowed_report_names` and `get_doctypes_with_read` don't support it.
	if stylo.session.user == "Administrator":
		return True

	if "System Manager" in stylo.get_roles():
		return True

	if doc.type == "Report" and doc.report_name in get_allowed_report_names():
		return True

	if doc.type == "Custom" and doc.document_type in get_doctypes_with_read():
		return True

	if doc.type == "Document Type" and doc.document_type in get_doctypes_with_read():
		return True

	return False


@stylo.whitelist()
def get_result(doc, filters, to_date=None):
	doc = stylo.parse_json(doc)
	fields = []
	sql_function_map = {
		"Count": "count",
		"Sum": "sum",
		"Average": "avg",
		"Minimum": "min",
		"Maximum": "max",
	}

	function = sql_function_map[doc.function]

	if function == "count":
		fields = [f"{function}(*) as result"]
	else:
		fields = [f"{function}({doc.aggregate_function_based_on}) as result"]

	if not filters:
		filters = []
	elif isinstance(filters, str):
		filters = stylo.parse_json(filters)

	if to_date:
		filters.append([doc.document_type, "creation", "<", to_date])

	res = stylo.get_list(
		doc.document_type, fields=fields, filters=filters, parent_doctype=doc.parent_document_type
	)
	number = res[0]["result"] if res else 0

	return flt(number)


@stylo.whitelist()
def get_percentage_difference(doc, filters, result):
	doc = stylo.parse_json(doc)
	result = stylo.parse_json(result)

	doc = stylo.get_doc("Number Card", doc.name)

	if not doc.get("show_percentage_stats"):
		return

	previous_result = calculate_previous_result(doc, filters)
	if previous_result == 0:
		return None
	else:
		if result == previous_result:
			return 0
		else:
			return ((result / previous_result) - 1) * 100.0


def calculate_previous_result(doc, filters):
	from stylo.utils import add_to_date

	current_date = stylo.utils.now()
	if doc.stats_time_interval == "Daily":
		previous_date = add_to_date(current_date, days=-1)
	elif doc.stats_time_interval == "Weekly":
		previous_date = add_to_date(current_date, weeks=-1)
	elif doc.stats_time_interval == "Monthly":
		previous_date = add_to_date(current_date, months=-1)
	else:
		previous_date = add_to_date(current_date, years=-1)

	number = get_result(doc, filters, previous_date)
	return number


@stylo.whitelist()
def create_number_card(args):
	args = stylo.parse_json(args)
	doc = stylo.new_doc("Number Card")

	doc.update(args)
	doc.insert(ignore_permissions=True)
	return doc


@stylo.whitelist()
@stylo.validate_and_sanitize_search_inputs
def get_cards_for_user(doctype, txt, searchfield, start, page_len, filters):
	meta = stylo.get_meta(doctype)
	searchfields = meta.get_search_fields()
	search_conditions = []

	if not stylo.db.exists("DocType", doctype):
		return

	numberCard = DocType("Number Card")

	if txt:
		search_conditions = [numberCard[field].like(f"%{txt}%") for field in searchfields]

	condition_query = stylo.qb.get_query(
		doctype,
		filters=filters,
		validate_filters=True,
	)

	return (
		condition_query.select(numberCard.name, numberCard.label, numberCard.document_type)
		.where((numberCard.owner == stylo.session.user) | (numberCard.is_public == 1))
		.where(Criterion.any(search_conditions))
	).run()


@stylo.whitelist()
def create_report_number_card(args):
	card = create_number_card(args)
	args = stylo.parse_json(args)
	args.name = card.name
	if args.dashboard:
		add_card_to_dashboard(stylo.as_json(args))


@stylo.whitelist()
def add_card_to_dashboard(args):
	args = stylo.parse_json(args)

	dashboard = stylo.get_doc("Dashboard", args.dashboard)
	dashboard_link = stylo.new_doc("Number Card Link")
	dashboard_link.card = args.name

	if args.set_standard and dashboard.is_standard:
		card = stylo.get_doc("Number Card", dashboard_link.card)
		card.is_standard = 1
		card.module = dashboard.module
		card.save()

	dashboard.append("cards", dashboard_link)
	dashboard.save()
