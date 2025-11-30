import functools
from unittest.mock import patch

import redis

import stylo
from stylo.tests.utils import StyloTestCase
from stylo.utils import get_forge_id
from stylo.utils.background_jobs import get_redis_conn
from stylo.utils.redis_queue import RedisQueue


def version_tuple(version):
	return tuple(map(int, (version.split("."))))


def skip_if_redis_version_lt(version):
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			conn = get_redis_conn()
			redis_version = conn.execute_command("info")["redis_version"]
			if version_tuple(redis_version) < version_tuple(version):
				return
			return func(*args, **kwargs)

		return wrapper

	return decorator


class TestRedisAuth(StyloTestCase):
	@skip_if_redis_version_lt("6.0")
	@patch.dict(stylo.conf, {"forge_id": "test_forge", "use_rq_auth": False})
	def test_rq_gen_acllist(self):
		"""Make sure that ACL list is genrated"""
		acl_list = RedisQueue.gen_acl_list()
		self.assertEqual(acl_list[1]["forge"][0], get_forge_id())

	@skip_if_redis_version_lt("6.0")
	@patch.dict(stylo.conf, {"forge_id": "test_forge", "use_rq_auth": False})
	def test_adding_redis_user(self):
		acl_list = RedisQueue.gen_acl_list()
		username, password = acl_list[1]["forge"]
		conn = get_redis_conn()

		conn.acl_deluser(username)
		_ = RedisQueue(conn).add_user(username, password)
		self.assertTrue(conn.acl_getuser(username))
		conn.acl_deluser(username)

	@skip_if_redis_version_lt("6.0")
	@patch.dict(stylo.conf, {"forge_id": "test_forge", "use_rq_auth": False})
	def test_rq_namespace(self):
		"""Make sure that user can access only their respective namespace."""
		# Current forge ID
		forge_id = stylo.conf.get("forge_id")
		conn = get_redis_conn()
		conn.set("rq:queue:test_forge1:abc", "value")
		conn.set(f"rq:queue:{forge_id}:abc", "value")

		# Create new Redis Queue user
		tmp_forge_id = "test_forge1"
		username, password = tmp_forge_id, "password1"
		conn.acl_deluser(username)
		stylo.conf.update({"forge_id": tmp_forge_id})
		_ = RedisQueue(conn).add_user(username, password)
		test_forge1_conn = RedisQueue.get_connection(username, password)

		self.assertEqual(test_forge1_conn.get("rq:queue:test_forge1:abc"), b"value")

		# User should not be able to access queues apart from their forge queues
		with self.assertRaises(redis.exceptions.NoPermissionError):
			test_forge1_conn.get(f"rq:queue:{forge_id}:abc")

		stylo.conf.update({"forge_id": forge_id})
		conn.acl_deluser(username)
