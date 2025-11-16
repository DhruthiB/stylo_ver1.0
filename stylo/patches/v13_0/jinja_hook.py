# Copyright (c) 2021, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from click import secho

import stylo


def execute():
	if stylo.get_hooks("jenv"):
		print()
		secho(
			'WARNING: The hook "jenv" is deprecated. Follow the migration guide to use the new "jinja" hook.',
			fg="yellow",
		)
		secho("https://github.com/stylo/stylo/wiki/Migrating-to-Version-13", fg="yellow")
		print()
