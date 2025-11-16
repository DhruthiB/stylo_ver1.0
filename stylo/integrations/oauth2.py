import json
from urllib.parse import quote, urlencode

from oauthlib.oauth2 import FatalClientError, OAuth2Error
from oauthlib.openid.connect.core.endpoints.pre_configured import Server as WebApplicationServer

import stylo
from stylo.integrations.doctype.oauth_provider_settings.oauth_provider_settings import (
	get_oauth_settings,
)
from stylo.oauth import (
	OAuthWebRequestValidator,
	generate_json_error_response,
	get_server_url,
	get_userinfo,
)


def get_oauth_server():
	if not getattr(stylo.local, "oauth_server", None):
		oauth_validator = OAuthWebRequestValidator()
		stylo.local.oauth_server = WebApplicationServer(oauth_validator)

	return stylo.local.oauth_server


def sanitize_kwargs(param_kwargs):
	"""Remove 'data' and 'cmd' keys, if present."""
	arguments = param_kwargs
	arguments.pop("data", None)
	arguments.pop("cmd", None)

	return arguments


def encode_params(params):
	"""
	Encode a dict of params into a query string.

	Use `quote_via=urllib.parse.quote` so that whitespaces will be encoded as
	`%20` instead of as `+`. This is needed because oauthlib cannot handle `+`
	as a whitespace.
	"""
	return urlencode(params, quote_via=quote)


@stylo.whitelist()
def approve(*args, **kwargs):
	r = stylo.request

	try:
		(
			scopes,
			stylo.flags.oauth_credentials,
		) = get_oauth_server().validate_authorization_request(r.url, r.method, r.get_data(), r.headers)

		headers, body, status = get_oauth_server().create_authorization_response(
			uri=stylo.flags.oauth_credentials["redirect_uri"],
			body=r.get_data(),
			headers=r.headers,
			scopes=scopes,
			credentials=stylo.flags.oauth_credentials,
		)
		uri = headers.get("Location", None)

		stylo.local.response["type"] = "redirect"
		stylo.local.response["location"] = uri
		return

	except (FatalClientError, OAuth2Error) as e:
		return generate_json_error_response(e)


@stylo.whitelist(allow_guest=True)
def authorize(**kwargs):
	success_url = "/api/method/stylo.integrations.oauth2.approve?" + encode_params(sanitize_kwargs(kwargs))
	failure_url = stylo.form_dict["redirect_uri"] + "?error=access_denied"

	if stylo.session.user == "Guest":
		# Force login, redirect to preauth again.
		stylo.local.response["type"] = "redirect"
		stylo.local.response["location"] = "/login?" + encode_params({"redirect-to": stylo.request.url})
	else:
		try:
			r = stylo.request
			(
				scopes,
				stylo.flags.oauth_credentials,
			) = get_oauth_server().validate_authorization_request(r.url, r.method, r.get_data(), r.headers)

			skip_auth = stylo.db.get_value(
				"OAuth Client",
				stylo.flags.oauth_credentials["client_id"],
				"skip_authorization",
			)
			unrevoked_tokens = stylo.get_all("OAuth Bearer Token", filters={"status": "Active"})

			if skip_auth or (get_oauth_settings().skip_authorization == "Auto" and unrevoked_tokens):
				stylo.local.response["type"] = "redirect"
				stylo.local.response["location"] = success_url
			else:
				if "openid" in scopes:
					scopes.remove("openid")
					scopes.extend(["Full Name", "Email", "User Image", "Roles"])

				# Show Allow/Deny screen.
				response_html_params = stylo._dict(
					{
						"client_id": stylo.db.get_value("OAuth Client", kwargs["client_id"], "app_name"),
						"success_url": success_url,
						"failure_url": failure_url,
						"details": scopes,
					}
				)
				resp_html = stylo.render_template(
					"templates/includes/oauth_confirmation.html", response_html_params
				)
				stylo.respond_as_web_page(stylo._("Confirm Access"), resp_html, primary_action=None)
		except (FatalClientError, OAuth2Error) as e:
			return generate_json_error_response(e)


@stylo.whitelist(allow_guest=True)
def get_token(*args, **kwargs):
	try:
		r = stylo.request
		headers, body, status = get_oauth_server().create_token_response(
			r.url, r.method, r.form, r.headers, stylo.flags.oauth_credentials
		)
		body = stylo._dict(json.loads(body))

		if body.error:
			stylo.local.response = body
			stylo.local.response["http_status_code"] = 400
			return

		stylo.local.response = body
		return

	except (FatalClientError, OAuth2Error) as e:
		return generate_json_error_response(e)


@stylo.whitelist(allow_guest=True)
def revoke_token(*args, **kwargs):
	try:
		r = stylo.request
		headers, body, status = get_oauth_server().create_revocation_response(
			r.url,
			headers=r.headers,
			body=r.form,
			http_method=r.method,
		)
	except (FatalClientError, OAuth2Error):
		pass

	# status_code must be 200
	stylo.local.response = stylo._dict({})
	stylo.local.response["http_status_code"] = status or 200
	return


@stylo.whitelist()
def openid_profile(*args, **kwargs):
	try:
		r = stylo.request
		headers, body, status = get_oauth_server().create_userinfo_response(
			r.url,
			headers=r.headers,
			body=r.form,
		)
		body = stylo._dict(json.loads(body))
		stylo.local.response = body
		return

	except (FatalClientError, OAuth2Error) as e:
		return generate_json_error_response(e)


@stylo.whitelist(allow_guest=True)
def openid_configuration():
	stylo_server_url = get_server_url()
	stylo.local.response = stylo._dict(
		{
			"issuer": stylo_server_url,
			"authorization_endpoint": f"{stylo_server_url}/api/method/stylo.integrations.oauth2.authorize",
			"token_endpoint": f"{stylo_server_url}/api/method/stylo.integrations.oauth2.get_token",
			"userinfo_endpoint": f"{stylo_server_url}/api/method/stylo.integrations.oauth2.openid_profile",
			"revocation_endpoint": f"{stylo_server_url}/api/method/stylo.integrations.oauth2.revoke_token",
			"introspection_endpoint": f"{stylo_server_url}/api/method/stylo.integrations.oauth2.introspect_token",
			"response_types_supported": [
				"code",
				"token",
				"code id_token",
				"code token id_token",
				"id_token",
				"id_token token",
			],
			"subject_types_supported": ["public"],
			"id_token_signing_alg_values_supported": ["HS256"],
		}
	)


@stylo.whitelist(allow_guest=True)
def introspect_token(token=None, token_type_hint=None):
	if token_type_hint not in ["access_token", "refresh_token"]:
		token_type_hint = "access_token"
	try:
		bearer_token = None
		if token_type_hint == "access_token":
			bearer_token = stylo.get_doc("OAuth Bearer Token", {"access_token": token})
		elif token_type_hint == "refresh_token":
			bearer_token = stylo.get_doc("OAuth Bearer Token", {"refresh_token": token})

		client = stylo.get_doc("OAuth Client", bearer_token.client)

		token_response = stylo._dict(
			{
				"client_id": client.client_id,
				"trusted_client": client.skip_authorization,
				"active": bearer_token.status == "Active",
				"exp": round(bearer_token.expiration_time.timestamp()),
				"scope": bearer_token.scopes,
			}
		)

		if "openid" in bearer_token.scopes:
			sub = stylo.get_value(
				"User Social Login",
				{"provider": "stylo", "parent": bearer_token.user},
				"userid",
			)

			if sub:
				token_response.update({"sub": sub})
				user = stylo.get_doc("User", bearer_token.user)
				userinfo = get_userinfo(user)
				token_response.update(userinfo)

		stylo.local.response = token_response

	except Exception:
		stylo.local.response = stylo._dict({"active": False})
