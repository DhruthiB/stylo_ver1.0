""" Utils for thread/process synchronization. """

import os
from contextlib import contextmanager

from filelock import FileLock as _StrongFileLock
from filelock import Timeout

import stylo
from stylo import _
from stylo.utils import get_forge_path, get_site_path
from stylo.utils.file_lock import LockTimeoutError

LOCKS_DIR = "locks"


@contextmanager
def filelock(lock_name: str, *, timeout=30, is_global=False):
	"""Create a lockfile to prevent concurrent operations acrosss processes.

	args:
	        lock_name: Unique name to identify a specific lock. Lockfile called `{name}.lock` will be
	        created.
	        timeout: time to wait before failing.
	        is_global: if set lock is global to forge

	Lock file location:
	        global - {forge_dir}/config/{name}.lock
	        site - {forge_dir}/sites/sitename/{name}.lock

	"""

	lock_filename = lock_name + ".lock"
	if not is_global:
		lock_path = os.path.abspath(get_site_path(LOCKS_DIR, lock_filename))
	else:
		lock_path = os.path.abspath(os.path.join(get_forge_path(), "config", lock_filename))

	try:
		with _StrongFileLock(lock_path, timeout=timeout):
			yield
	except Timeout as e:
		stylo.log_error("Filelock: Failed to aquire {lock_path}")

		raise LockTimeoutError(
			_("Failed to aquire lock: {}").format(lock_name)
			+ "<br>"
			+ _("You can manually remove the lock if you think it's safe: {}").format(lock_path)
		) from e
