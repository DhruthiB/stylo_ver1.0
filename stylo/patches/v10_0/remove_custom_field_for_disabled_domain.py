import stylo


def execute():
	stylo.reload_doc("core", "doctype", "domain")
	stylo.reload_doc("core", "doctype", "has_domain")
	active_domains = stylo.get_active_domains()
	all_domains = stylo.get_all("Domain")

	for d in all_domains:
		if d.name not in active_domains:
			inactive_domain = stylo.get_doc("Domain", d.name)
			inactive_domain.setup_data()
			inactive_domain.remove_custom_field()
