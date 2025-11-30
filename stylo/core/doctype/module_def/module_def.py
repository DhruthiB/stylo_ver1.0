# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json
import os

import stylo
from stylo.model.document import Document
from stylo.modules.export_file import delete_folder


class ModuleDef(Document):
	def on_update(self):
		"""If in `developer_mode`, create folder for module and
		add in `modules.txt` of app if missing."""
		stylo.clear_cache()
		if not self.custom and stylo.conf.get("developer_mode"):
			self.create_modules_folder()
			self.add_to_modules_txt()

	def create_modules_folder(self):
		"""Creates a folder `[app]/[module]` and adds `__init__.py`"""
		module_path = stylo.get_app_path(self.app_name, self.name)
		if not os.path.exists(module_path):
			os.mkdir(module_path)
			with open(os.path.join(module_path, "__init__.py"), "w") as f:
				f.write("")

	def add_to_modules_txt(self):
		"""Adds to `[app]/modules.txt`"""
		modules = None
		if not stylo.local.module_app.get(stylo.scrub(self.name)):
			with open(stylo.get_app_path(self.app_name, "modules.txt")) as f:
				content = f.read()
				if self.name not in content.splitlines():
					modules = list(filter(None, content.splitlines()))
					modules.append(self.name)

			if modules:
				with open(stylo.get_app_path(self.app_name, "modules.txt"), "w") as f:
					f.write("\n".join(modules))

				stylo.clear_cache()
				stylo.setup_module_map()

	def on_trash(self):
		"""Delete module name from modules.txt"""

		if not stylo.conf.get("developer_mode") or stylo.flags.in_uninstall or self.custom:
			return

		modules = None
		if stylo.local.module_app.get(stylo.scrub(self.name)):
			delete_folder(self.module_name, "Module Def", self.name)
			with open(stylo.get_app_path(self.app_name, "modules.txt")) as f:
				content = f.read()
				if self.name in content.splitlines():
					modules = list(filter(None, content.splitlines()))
					modules.remove(self.name)

			if modules:
				with open(stylo.get_app_path(self.app_name, "modules.txt"), "w") as f:
					f.write("\n".join(modules))

				stylo.clear_cache()
				stylo.setup_module_map()


@stylo.whitelist()
def get_installed_apps():
	return json.dumps(stylo.get_installed_apps())
