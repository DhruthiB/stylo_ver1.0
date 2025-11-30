# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo
import stylo.monitor
from stylo.monitor import MONITOR_REDIS_KEY, get_trace_id
from stylo.tests.utils import StyloTestCase
from stylo.utils import set_request
from stylo.utils.response import build_response


class TestMonitor(StyloTestCase):
	def setUp(self):
		stylo.conf.monitor = 1
		stylo.cache().delete_value(MONITOR_REDIS_KEY)

	def tearDown(self):
		stylo.conf.monitor = 0
		stylo.cache().delete_value(MONITOR_REDIS_KEY)

	def test_enable_monitor(self):
		set_request(method="GET", path="/api/method/stylo.ping")
		response = build_response("json")

		stylo.monitor.start()
		stylo.monitor.stop(response)

		logs = stylo.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = stylo.parse_json(logs[0].decode())
		self.assertTrue(log.duration)
		self.assertTrue(log.site)
		self.assertTrue(log.timestamp)
		self.assertTrue(log.uuid)
		self.assertTrue(log.request)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_no_response(self):
		set_request(method="GET", path="/api/method/stylo.ping")

		stylo.monitor.start()
		stylo.monitor.stop(response=None)

		logs = stylo.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = stylo.parse_json(logs[0].decode())
		self.assertEqual(log.request["status_code"], 500)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_job(self):
		stylo.utils.background_jobs.execute_job(
			stylo.local.site, "stylo.ping", None, None, {}, is_async=False
		)

		logs = stylo.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)
		log = stylo.parse_json(logs[0].decode())
		self.assertEqual(log.transaction_type, "job")
		self.assertTrue(log.job)
		self.assertEqual(log.job["method"], "stylo.ping")
		self.assertEqual(log.job["scheduled"], False)
		self.assertEqual(log.job["wait"], 0)

	def test_flush(self):
		set_request(method="GET", path="/api/method/stylo.ping")
		response = build_response("json")
		stylo.monitor.start()
		stylo.monitor.stop(response)

		open(stylo.monitor.log_file(), "w").close()
		stylo.monitor.flush()

		with open(stylo.monitor.log_file()) as f:
			logs = f.readlines()

		self.assertEqual(len(logs), 1)
		log = stylo.parse_json(logs[0])
		self.assertEqual(log.transaction_type, "request")

	def test_trace_ids(self):
		set_request(method="GET", path="/api/method/stylo.ping")
		response = build_response("json")
		stylo.monitor.start()
		stylo.db.sql("select 1")
		self.assertIn(get_trace_id(), str(stylo.db.last_query))
		stylo.monitor.stop(response)
