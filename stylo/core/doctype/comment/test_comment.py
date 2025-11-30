# Copyright (c) 2019, Stylo Technologies and Contributors
# License: MIT. See LICENSE
import json

import stylo
from stylo.templates.includes.comments.comments import add_comment
from stylo.tests.test_model_utils import set_user
from stylo.tests.utils import StyloTestCase, change_settings
from stylo.website.doctype.blog_post.test_blog_post import make_test_blog


class TestComment(StyloTestCase):
	def tearDown(self):
		stylo.form_dict.comment = None
		stylo.form_dict.comment_email = None
		stylo.form_dict.comment_by = None
		stylo.form_dict.reference_doctype = None
		stylo.form_dict.reference_name = None
		stylo.form_dict.route = None
		stylo.local.request_ip = None

	def test_comment_creation(self):
		test_doc = stylo.get_doc(dict(doctype="ToDo", description="test"))
		test_doc.insert()
		comment = test_doc.add_comment("Comment", "test comment")

		test_doc.reload()

		# check if updated in _comments cache
		comments = json.loads(test_doc.get("_comments"))
		self.assertEqual(comments[0].get("name"), comment.name)
		self.assertEqual(comments[0].get("comment"), comment.content)

		# check document creation
		comment_1 = stylo.get_all(
			"Comment",
			fields=["*"],
			filters=dict(reference_doctype=test_doc.doctype, reference_name=test_doc.name),
		)[0]

		self.assertEqual(comment_1.content, "test comment")

	# test via blog
	def test_public_comment(self):
		test_blog = make_test_blog()

		stylo.db.delete("Comment", {"reference_doctype": "Blog Post"})

		stylo.form_dict.comment = "Good comment with 10 chars"
		stylo.form_dict.comment_email = "test@test.com"
		stylo.form_dict.comment_by = "Good Tester"
		stylo.form_dict.reference_doctype = "Blog Post"
		stylo.form_dict.reference_name = test_blog.name
		stylo.form_dict.route = test_blog.route
		stylo.local.request_ip = "127.0.0.1"

		add_comment()

		self.assertEqual(
			stylo.get_all(
				"Comment",
				fields=["*"],
				filters=dict(reference_doctype=test_blog.doctype, reference_name=test_blog.name),
			)[0].published,
			1,
		)

		stylo.db.delete("Comment", {"reference_doctype": "Blog Post"})

		stylo.form_dict.comment = "pleez vizits my site http://mysite.com"
		stylo.form_dict.comment_by = "bad commentor"

		add_comment()

		self.assertEqual(
			len(
				stylo.get_all(
					"Comment",
					fields=["*"],
					filters=dict(reference_doctype=test_blog.doctype, reference_name=test_blog.name),
				)
			),
			0,
		)

		# test for filtering html and css injection elements
		stylo.db.delete("Comment", {"reference_doctype": "Blog Post"})

		stylo.form_dict.comment = "<script>alert(1)</script>Comment"
		stylo.form_dict.comment_by = "hacker"

		add_comment()

		self.assertEqual(
			stylo.get_all(
				"Comment",
				fields=["content"],
				filters=dict(reference_doctype=test_blog.doctype, reference_name=test_blog.name),
			)[0]["content"],
			"Comment",
		)

		test_blog.delete()

	@change_settings("Blog Settings", {"allow_guest_to_comment": 0})
	def test_guest_cannot_comment(self):
		test_blog = make_test_blog()
		with set_user("Guest"):
			stylo.form_dict.comment = "Good comment with 10 chars"
			stylo.form_dict.comment_email = "mail@example.org"
			stylo.form_dict.comment_by = "Good Tester"
			stylo.form_dict.reference_doctype = "Blog Post"
			stylo.form_dict.reference_name = test_blog.name
			stylo.form_dict.route = test_blog.route
			stylo.local.request_ip = "127.0.0.1"

			self.assertEqual(add_comment(), None)

	def test_user_not_logged_in(self):
		some_system_user = stylo.db.get_value("User", {})

		test_blog = make_test_blog()
		with set_user("Guest"):
			stylo.form_dict.comment = "Good comment with 10 chars"
			stylo.form_dict.comment_email = some_system_user
			stylo.form_dict.comment_by = "Good Tester"
			stylo.form_dict.reference_doctype = "Blog Post"
			stylo.form_dict.reference_name = test_blog.name
			stylo.form_dict.route = test_blog.route
			stylo.local.request_ip = "127.0.0.1"

			self.assertRaises(stylo.ValidationError, add_comment)
