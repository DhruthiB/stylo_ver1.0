# Copyright (c) 2021, Stylo Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import functools

import stylo


@stylo.whitelist()
def get_google_fonts():
	return _get_google_fonts()


@functools.lru_cache
def _get_google_fonts():
	file_path = stylo.get_app_path("stylo", "data", "google_fonts.json")
	return stylo.parse_json(stylo.read_file(file_path))
