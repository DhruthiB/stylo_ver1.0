import stylo


def execute():
	stylo.reload_doc("website", "doctype", "web_page_view", force=True)
	stylo.db.sql("""UPDATE `tabWeb Page View` set path='/' where path=''""")
