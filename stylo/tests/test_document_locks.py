# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import stylo
from stylo.tests.utils import StyloTestCase
from stylo.utils.data import add_to_date, today


class TestDocumentLocks(StyloTestCase):
	def test_locking(self):
		todo = stylo.get_doc(dict(doctype="ToDo", description="test")).insert()
		todo_1 = stylo.get_doc("ToDo", todo.name)

		todo.lock()
		self.assertRaises(stylo.DocumentLockedError, todo_1.lock)
		todo.unlock()

		todo_1.lock()
		self.assertRaises(stylo.DocumentLockedError, todo.lock)
		todo_1.unlock()

	def test_locks_auto_expiry(self):
		todo = stylo.get_doc(dict(doctype="ToDo", description=stylo.generate_hash())).insert()
		todo.lock()

		self.assertRaises(stylo.DocumentLockedError, todo.lock)

		with self.freeze_time(add_to_date(today(), days=3)):
			todo.lock()
