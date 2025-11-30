# Copyright (c) 2022, Stylo Technologies and Contributors
# See license.txt

import stylo
from stylo.core.doctype.rq_worker.rq_worker import RQWorker
from stylo.tests.utils import StyloTestCase


class TestRQWorker(StyloTestCase):
	def test_get_worker_list(self):
		workers = RQWorker.get_list({})
		self.assertGreaterEqual(len(workers), 1)
		self.assertTrue(any("short" in w.queue_type for w in workers))

	def test_worker_serialization(self):
		workers = RQWorker.get_list({})
		stylo.get_doc("RQ Worker", workers[0].name)
