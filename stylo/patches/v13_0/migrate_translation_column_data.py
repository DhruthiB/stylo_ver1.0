import stylo


def execute():
	stylo.reload_doctype("Translation")
	stylo.db.sql(
		"UPDATE `tabTranslation` SET `translated_text`=`target_name`, `source_text`=`source_name`, `contributed`=0"
	)
