# Copyright (c) 2021, Stylo Technologies and contributors
# License: MIT. See LICENSE

import json

import stylo
from stylo.model.document import Document
from stylo.modules.export_file import export_to_files


class FormTour(Document):
	def before_save(self):
		if self.is_standard and not self.module:
			if self.workspace_name:
				self.module = stylo.db.get_value("Workspace", self.workspace_name, "module")
			elif self.dashboard_name:
				dashboard_doctype = stylo.db.get_value("Dashboard", self.dashboard_name, "module")
				self.module = stylo.db.get_value("DocType", dashboard_doctype, "module")
			else:
				self.module = "Desk"
		if not self.ui_tour:
			meta = stylo.get_meta(self.reference_doctype)
			for step in self.steps:
				if step.is_table_field and step.parent_fieldname:
					parent_field_df = meta.get_field(step.parent_fieldname)
					step.child_doctype = parent_field_df.options
					field_df = stylo.get_meta(step.child_doctype).get_field(step.fieldname)
					step.label = field_df.label
					step.fieldtype = field_df.fieldtype
				else:
					field_df = meta.get_field(step.fieldname)
					step.label = field_df.label
					step.fieldtype = field_df.fieldtype

	def on_update(self):
		stylo.cache().delete_key("bootinfo")

		if stylo.conf.developer_mode and self.is_standard:
			export_to_files([["Form Tour", self.name]], self.module)

	def on_trash(self):
		stylo.cache().delete_key("bootinfo")


@stylo.whitelist()
def reset_tour(tour_name):
	for user in stylo.get_all("User"):
		user_doc = stylo.get_doc("User", user.name)
		onboarding_status = stylo.parse_json(user_doc.onboarding_status)
		onboarding_status.pop(tour_name, None)
		user_doc.onboarding_status = stylo.as_json(onboarding_status)
		user_doc.save()


@stylo.whitelist()
def update_user_status(value, step):
	from stylo.utils.telemetry import capture

	step = stylo.parse_json(step)
	tour = stylo.parse_json(value)

	capture(
		stylo.scrub(f"{step.parent}_{step.title}"),
		app="stylo_ui_tours",
		properties={"is_completed": tour.is_completed},
	)
	stylo.db.set_value("User", stylo.session.user, "onboarding_status", value, update_modified=False)

	stylo.cache().hdel("bootinfo", stylo.session.user)


def get_onboarding_ui_tours():
	if not stylo.get_system_settings("enable_onboarding"):
		return []

	ui_tours = stylo.get_all("Form Tour", filters={"ui_tour": 1}, fields=["page_route", "name"])

	return [[tour.name, json.loads(tour.page_route)] for tour in ui_tours]
