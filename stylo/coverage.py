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
	"*/test_*",
	"*/node_modules/*",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]

Stylo_EXCLUSIONS = [
	"*/tests/*",
	"*/commands/*",
	"*/stylo/change_log/*",
	"*/stylo/exceptions*",
	"*/stylo/coverage.py",
	"*stylo/setup.py",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]


class CodeCoverage:
	def __init__(self, with_coverage, app):
		self.with_coverage = with_coverage
		self.app = app or "stylo"

	def __enter__(self):
		if self.with_coverage:
			import os

			from coverage import Coverage

			from stylo.utils import get_forge_path

			# Generate coverage report only for app that is being tested
			source_path = os.path.join(get_forge_path(), "apps", self.app)
			omit = STANDARD_EXCLUSIONS[:]

			if self.app == "stylo":
				omit.extend(Stylo_EXCLUSIONS)

			self.coverage = Coverage(source=[source_path], omit=omit, include=STANDARD_INCLUSIONS)
			self.coverage.start()

	def __exit__(self, exc_type, exc_value, traceback):
		if self.with_coverage:
			self.coverage.stop()
			self.coverage.save()
			self.coverage.xml_report()
