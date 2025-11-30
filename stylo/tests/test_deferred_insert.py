import stylo
from stylo.deferred_insert import deferred_insert, save_to_db
from stylo.tests.utils import StyloTestCase


class TestDeferredInsert(StyloTestCase):
	def test_deferred_insert(self):
		route_history = {"route": stylo.generate_hash(), "user": "Administrator"}
		deferred_insert("Route History", [route_history])

		save_to_db()
		self.assertTrue(stylo.db.exists("Route History", route_history))
