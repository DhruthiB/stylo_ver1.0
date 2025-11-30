# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import stylo
from stylo import _
from stylo.model.document import Document


class Blogger(Document):
	def validate(self):
		if self.user and not stylo.db.exists("User", self.user):
			# for data import
			stylo.get_doc(
				{"doctype": "User", "email": self.user, "first_name": self.user.split("@", 1)[0]}
			).insert()

	def on_update(self):
		"if user is set, then update all older blogs"

		from stylo.website.doctype.blog_post.blog_post import clear_blog_cache

		clear_blog_cache()

		if self.user:
			for blog in stylo.db.sql_list(
				"""select name from `tabBlog Post` where owner=%s
				and ifnull(blogger,'')=''""",
				self.user,
			):
				b = stylo.get_doc("Blog Post", blog)
				b.blogger = self.name
				b.save()

			stylo.permissions.add_user_permission("Blogger", self.name, self.user)
