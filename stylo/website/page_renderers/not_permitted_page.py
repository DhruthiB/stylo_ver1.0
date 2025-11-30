from urllib.parse import quote_plus

import stylo
from stylo import _
from stylo.utils import cstr
from stylo.website.page_renderers.template_page import TemplatePage


class NotPermittedPage(TemplatePage):
	def __init__(self, path=None, http_status_code=None, exception=""):
		stylo.local.message = cstr(exception)
		super().__init__(path=path, http_status_code=http_status_code)
		self.http_status_code = 403

	def can_render(self):
		return True

	def render(self):
		action = f"/login?redirect-to={quote_plus(stylo.request.path)}"
		if stylo.request.path.startswith("/app"):
			action = "/login"
		stylo.local.message_title = _("Not Permitted")
		stylo.local.response["context"] = dict(
			indicator_color="red", primary_action=action, primary_label=_("Login"), fullpage=True
		)
		self.set_standard_path("message")
		return super().render()
