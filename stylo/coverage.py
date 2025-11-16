# Copyright (c) 2021, Stylo Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE
"""
stylo.coverage
~~~~~~~~~~~~~~~~

Coverage settings for stylo
"""

STANDARD_INCLUSIONS = ["*.py"]

STANDARD_EXCLUSIONS = [
	"*.js",
	"*.xml",
	"*.pyc",
	"*.css",
	"*.less",
	"*.scss",
	"*.vue",
	"*.html",
	"*/test_*/*",
	"*/node_modules/*",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]

# tested via commands' test suite
TESTED_VIA_CLI = [
	"*/stylo/installer.py",
	"*/stylo/utils/install.py",
	"*/stylo/utils/scheduler.py",
	"*/stylo/utils/doctor.py",
	"*/stylo/build.py",
	"*/stylo/database/__init__.py",
	"*/stylo/database/db_manager.py",
	"*/stylo/database/**/setup_db.py",
]

FRAPPE_EXCLUSIONS = [
	"*/tests/*",
	"*/commands/*",
	"*/stylo/change_log/*",
	"*/stylo/exceptions*",
	"*/stylo/desk/page/setup_wizard/setup_wizard.py",
	"*/stylo/coverage.py",
	"*stylo/setup.py",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
	*TESTED_VIA_CLI,
]


class CodeCoverage:
	"""
	Context manager for handling code coverage.

	This class sets up code coverage measurement for a specific app,
	applying the appropriate inclusion and exclusion patterns.
	"""

	def __init__(self, with_coverage, app, outfile="coverage.xml"):
		self.with_coverage = with_coverage
		self.app = app or "stylo"
		self.outfile = outfile

	def __enter__(self):
		if self.with_coverage:
			import os

			from coverage import Coverage

			from stylo.utils import get_forge_path

			# Generate coverage report only for app that is being tested
			source_path = os.path.join(get_forge_path(), "apps", self.app)
			omit = STANDARD_EXCLUSIONS[:]

			if self.app == "stylo":
				omit.extend(FRAPPE_EXCLUSIONS)

			self.coverage = Coverage(source=[source_path], omit=omit, include=STANDARD_INCLUSIONS)
			self.coverage.start()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if self.with_coverage:
			self.coverage.stop()
			self.coverage.save()
			self.coverage.xml_report(outfile=self.outfile)
			print("Saved Coverage")
