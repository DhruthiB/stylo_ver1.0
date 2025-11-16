import stylo


def execute():
	stylo.reload_doc("website", "doctype", "web_page_view", force=True)
	site_url = stylo.utils.get_site_url(stylo.local.site)
	stylo.db.sql(f"""UPDATE `tabWeb Page View` set is_unique=1 where referrer LIKE '%{site_url}%'""")
