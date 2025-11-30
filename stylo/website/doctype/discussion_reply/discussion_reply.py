# Copyright (c) 2021, Stylo Technologies and contributors
# For license information, please see license.txt

import stylo
from stylo.model.document import Document
from stylo.realtime import get_website_room


class DiscussionReply(Document):
	def on_update(self):
		stylo.publish_realtime(
			event="update_message",
			room=get_website_room(),
			message={"reply": stylo.utils.md_to_html(self.reply), "reply_name": self.name},
			after_commit=True,
		)

	def after_insert(self):
		replies = stylo.db.count("Discussion Reply", {"topic": self.topic})
		topic_info = stylo.get_all(
			"Discussion Topic",
			{"name": self.topic},
			["reference_doctype", "reference_docname", "name", "title", "owner", "creation"],
		)

		template = stylo.render_template(
			"stylo/templates/discussions/reply_card.html",
			{
				"reply": self,
				"topic": {"name": self.topic},
				"loop": {"index": replies},
				"single_thread": True if not topic_info[0].title else False,
			},
		)

		sidebar = stylo.render_template(
			"stylo/templates/discussions/sidebar.html", {"topic": topic_info[0]}
		)

		new_topic_template = stylo.render_template(
			"stylo/templates/discussions/reply_section.html", {"topic": topic_info[0]}
		)

		stylo.publish_realtime(
			event="publish_message",
			room=get_website_room(),
			message={
				"template": template,
				"topic_info": topic_info[0],
				"sidebar": sidebar,
				"new_topic_template": new_topic_template,
				"reply_owner": self.owner,
			},
			after_commit=True,
		)

	def after_delete(self):
		stylo.publish_realtime(
			event="delete_message",
			room=get_website_room(),
			message={"reply_name": self.name},
			after_commit=True,
		)


@stylo.whitelist()
def delete_message(reply_name):
	owner = stylo.db.get_value("Discussion Reply", reply_name, "owner")
	if owner == stylo.session.user:
		stylo.delete_doc("Discussion Reply", reply_name)
