import stylo


def update_system_settings(args, commit=False):
	doc = stylo.get_doc("System Settings")
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
	if commit:
		stylo.db.commit()


def get_system_setting(key):
	return stylo.db.get_single_value("System Settings", key)


global_test_dependencies = ["User"]
