import click

import stylo


def execute():
	stylo.delete_doc_if_exists("DocType", "Chat Message")
	stylo.delete_doc_if_exists("DocType", "Chat Message Attachment")
	stylo.delete_doc_if_exists("DocType", "Chat Profile")
	stylo.delete_doc_if_exists("DocType", "Chat Token")
	stylo.delete_doc_if_exists("DocType", "Chat Room User")
	stylo.delete_doc_if_exists("DocType", "Chat Room")
	stylo.delete_doc_if_exists("Module Def", "Chat")

	click.secho(
		"Chat Module is moved to a separate app and is removed from Stylo in version-13.\n"
		"Please install the app to continue using the chat feature: https://github.com/stylo/chat",
		fg="yellow",
	)
