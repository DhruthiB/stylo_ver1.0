import stylo
from stylo.utils import cint


def execute():
	stylo.reload_doctype("Dropbox Settings")
	check_dropbox_enabled = cint(stylo.db.get_single_value("Dropbox Settings", "enabled"))
	if check_dropbox_enabled == 1:
		stylo.db.set_single_value("Dropbox Settings", "file_backup", 1)
