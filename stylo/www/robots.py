import stylo

base_template_path = "www/robots.txt"


def get_context(context):
	robots_txt = (
		stylo.db.get_single_value("Website Settings", "robots_txt")
		or (stylo.local.conf.robots_txt and stylo.read_file(stylo.local.conf.robots_txt))
		or ""
	)

	return {"robots_txt": robots_txt}
