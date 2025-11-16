import stylo


def execute():
	stylo.delete_doc_if_exists("DocType", "Post")
	stylo.delete_doc_if_exists("DocType", "Post Comment")
