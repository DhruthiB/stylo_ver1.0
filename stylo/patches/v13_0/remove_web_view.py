import stylo


def execute():
	stylo.delete_doc_if_exists("DocType", "Web View")
	stylo.delete_doc_if_exists("DocType", "Web View Component")
	stylo.delete_doc_if_exists("DocType", "CSS Class")
