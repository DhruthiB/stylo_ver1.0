# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import time

from werkzeug.wrappers import Response

import stylo
import stylo.rate_limiter
from stylo.rate_limiter import RateLimiter
from stylo.tests.utils import StyloTestCase
from stylo.utils import cint


class TestRateLimiter(StyloTestCase):
	def test_apply_with_limit(self):
		stylo.conf.rate_limit = {"window": 86400, "limit": 1}
		stylo.rate_limiter.apply()

		self.assertTrue(hasattr(stylo.local, "rate_limiter"))
		self.assertIsInstance(stylo.local.rate_limiter, RateLimiter)

		stylo.cache().delete(stylo.local.rate_limiter.key)
		delattr(stylo.local, "rate_limiter")

	def test_apply_without_limit(self):
		stylo.conf.rate_limit = None
		stylo.rate_limiter.apply()

		self.assertFalse(hasattr(stylo.local, "rate_limiter"))

	def test_respond_over_limit(self):
		limiter = RateLimiter(1, 86400)
		time.sleep(1)
		limiter.update()

		stylo.conf.rate_limit = {"window": 86400, "limit": 1}
		self.assertRaises(stylo.TooManyRequestsError, stylo.rate_limiter.apply)
		stylo.rate_limiter.update()

		response = stylo.rate_limiter.respond()

		self.assertIsInstance(response, Response)
		self.assertEqual(response.status_code, 429)

		headers = stylo.local.rate_limiter.headers()
		self.assertIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertIn("X-RateLimit-Limit", headers)
		self.assertIn("X-RateLimit-Remaining", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"]) <= 86400)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 1000000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 0)

		stylo.cache().delete(limiter.key)
		stylo.cache().delete(stylo.local.rate_limiter.key)
		delattr(stylo.local, "rate_limiter")

	def test_respond_under_limit(self):
		stylo.conf.rate_limit = {"window": 86400, "limit": 0.01}
		stylo.rate_limiter.apply()
		stylo.rate_limiter.update()
		response = stylo.rate_limiter.respond()
		self.assertEqual(response, None)

		stylo.cache().delete(stylo.local.rate_limiter.key)
		delattr(stylo.local, "rate_limiter")

	def test_headers_under_limit(self):
		stylo.conf.rate_limit = {"window": 86400, "limit": 1}
		stylo.rate_limiter.apply()
		stylo.rate_limiter.update()
		headers = stylo.local.rate_limiter.headers()
		self.assertNotIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"] < 86400))
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 1000000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 1000000)

		stylo.cache().delete(stylo.local.rate_limiter.key)
		delattr(stylo.local, "rate_limiter")

	def test_reject_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.01, 86400)
		self.assertRaises(stylo.TooManyRequestsError, limiter.apply)

		stylo.cache().delete(limiter.key)

	def test_do_not_reject_under_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.02, 86400)
		self.assertEqual(limiter.apply(), None)

		stylo.cache().delete(limiter.key)

	def test_update_method(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		self.assertEqual(limiter.duration, cint(stylo.cache().get(limiter.key)))

		stylo.cache().delete(limiter.key)
