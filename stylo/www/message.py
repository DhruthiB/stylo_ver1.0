# Copyright (c) 2015, Stylo Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import stylo
from stylo.utils import strip_html_tags
from stylo.utils.html_utils import clean_html

no_cache = 1


def get_context(context):
	message_context = stylo._dict()
	if hasattr(stylo.local, "message"):
		message_context["header"] = stylo.local.message_title
		message_context["title"] = strip_html_tags(stylo.local.message_title)
		message_context["message"] = stylo.local.message
		if hasattr(stylo.local, "message_success"):
			message_context["success"] = stylo.local.message_success

	elif stylo.local.form_dict.id:
		message_id = stylo.local.form_dict.id
		key = f"message_id:{message_id}"
		message = stylo.cache().get_value(key, expires=True)
		if message:
			message_context.update(message.get("context", {}))
			if message.get("http_status_code"):
				stylo.local.response["http_status_code"] = message["http_status_code"]

	if not message_context.title:
		message_context.title = clean_html(stylo.form_dict.title)

	if not message_context.message:
		message_context.message = clean_html(stylo.form_dict.message)

	return message_context
