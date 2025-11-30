# Copyright (c) 2020, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json
import os
import traceback
import uuid
from datetime import datetime

import rq

import stylo
from stylo.utils.data import cint
from stylo.utils.synchronization import filelock

MONITOR_REDIS_KEY = "monitor-transactions"
MONITOR_MAX_ENTRIES = 1000000


def start(transaction_type="request", method=None, kwargs=None):
	if stylo.conf.monitor:
		stylo.local.monitor = Monitor(transaction_type, method, kwargs)


def stop(response=None):
	if hasattr(stylo.local, "monitor"):
		stylo.local.monitor.dump(response)


def add_data_to_monitor(**kwargs) -> None:
	"""Add additional custom key-value pairs along with monitor log.
	Note: Key-value pairs should be simple JSON exportable types."""
	if hasattr(stylo.local, "monitor"):
		stylo.local.monitor.add_custom_data(**kwargs)


def get_trace_id() -> str | None:
	"""Get unique ID for current transaction."""
	if monitor := getattr(stylo.local, "monitor", None):
		return monitor.data.uuid


def log_file():
	return os.path.join(stylo.utils.get_forge_path(), "logs", "monitor.json.log")


class Monitor:
	__slots__ = ("data",)

	def __init__(self, transaction_type, method, kwargs):
		try:
			self.data = stylo._dict(
				{
					"site": stylo.local.site,
					"timestamp": datetime.utcnow(),
					"transaction_type": transaction_type,
					"uuid": str(uuid.uuid4()),
				}
			)

			if transaction_type == "request":
				self.collect_request_meta()
			else:
				self.collect_job_meta(method, kwargs)
		except Exception:
			traceback.print_exc()

	def collect_request_meta(self):
		self.data.request = stylo._dict(
			{
				"ip": stylo.local.request_ip,
				"method": stylo.request.method,
				"path": stylo.request.path,
			}
		)

	def collect_job_meta(self, method, kwargs):
		self.data.job = stylo._dict({"method": method, "scheduled": False, "wait": 0})
		if "run_scheduled_job" in method:
			self.data.job.method = kwargs["job_type"]
			self.data.job.scheduled = True

		job = rq.get_current_job()
		if job:
			self.data.uuid = job.id
			waitdiff = self.data.timestamp - job.enqueued_at
			self.data.job.wait = int(waitdiff.total_seconds() * 1000000)

	def add_custom_data(self, **kwargs):
		if self.data:
			self.data.update(kwargs)

	def dump(self, response=None):
		try:
			timediff = datetime.utcnow() - self.data.timestamp
			# Obtain duration in microseconds
			self.data.duration = int(timediff.total_seconds() * 1000000)

			if self.data.transaction_type == "request":
				if response:
					self.data.request.status_code = response.status_code
					self.data.request.response_length = int(response.headers.get("Content-Length", 0))
				else:
					self.data.request.status_code = 500

				if hasattr(stylo.local, "rate_limiter"):
					limiter = stylo.local.rate_limiter
					self.data.request.counter = limiter.counter
					if limiter.rejected:
						self.data.request.reset = limiter.reset

			self.store()
		except Exception:
			traceback.print_exc()

	def store(self):
		serialized = json.dumps(self.data, sort_keys=True, default=str, separators=(",", ":"))
		length = stylo.cache().rpush(MONITOR_REDIS_KEY, serialized)
		if cint(length) > MONITOR_MAX_ENTRIES:
			stylo.cache().ltrim(MONITOR_REDIS_KEY, 1, -1)


def flush():
	logs = stylo.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
	if not logs:
		return

	logs = list(map(stylo.safe_decode, logs))
	with filelock("monitor_flush", is_global=True, timeout=5):
		with open(log_file(), "a") as f:
			f.write("\n".join(logs))
			f.write("\n")

	# Remove fetched entries from cache
	stylo.cache().ltrim(MONITOR_REDIS_KEY, len(logs) - 1, -1)
