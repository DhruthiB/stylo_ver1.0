from . import __version__ as app_version

app_name = "stylo"
app_title = "Stylo Framework"
app_publisher = "Stylo Technologies"
app_description = "Full stack web framework with Python, Javascript, MariaDB, Redis, Node"
source_link = "https://github.com/stylo/stylo"
app_license = "MIT"
app_logo_url = "/assets/stylo/images/stylo-framework-logo.svg"

develop_version = "14.x.x-develop"

app_email = "developers@stylo.io"

docs_app = "stylo_docs"

before_install = "stylo.utils.install.before_install"
after_install = "stylo.utils.install.after_install"

page_js = {"setup-wizard": "public/js/stylo/setup_wizard.js"}

# website
app_include_js = [
	"libs.bundle.js",
	"desk.bundle.js",
	"list.bundle.js",
	"form.bundle.js",
	"controls.bundle.js",
	"report.bundle.js",
	"telemetry.bundle.js",
]
app_include_css = [
	"desk.bundle.css",
	"report.bundle.css",
]

doctype_js = {
	"Web Page": "public/js/stylo/utils/web_template.js",
	"Website Settings": "public/js/stylo/utils/web_template.js",
}

web_include_js = ["website_script.js"]

web_include_css = []

email_css = ["email.bundle.css"]

website_route_rules = [
	{"from_route": "/blog/<category>", "to_route": "Blog Post"},
	{"from_route": "/kb/<category>", "to_route": "Help Article"},
	{"from_route": "/newsletters", "to_route": "Newsletter"},
	{"from_route": "/profile", "to_route": "me"},
	{"from_route": "/app/<path:app_path>", "to_route": "app"},
]

website_redirects = [
	{"source": r"/desk(.*)", "target": r"/app\1"},
]

base_template = "templates/base.html"

write_file_keys = ["file_url", "file_name"]

notification_config = "stylo.core.notifications.get_notification_config"

before_tests = "stylo.utils.install.before_tests"

email_append_to = ["Event", "ToDo", "Communication"]

calendars = ["Event"]

leaderboards = "stylo.desk.leaderboard.get_leaderboards"

# login

on_session_creation = [
	"stylo.core.doctype.activity_log.feed.login_feed",
	"stylo.core.doctype.user.user.notify_admin_access_to_system_manager",
]

on_logout = "stylo.core.doctype.session_default_settings.session_default_settings.clear_session_defaults"

# permissions

permission_query_conditions = {
	"Event": "stylo.desk.doctype.event.event.get_permission_query_conditions",
	"ToDo": "stylo.desk.doctype.todo.todo.get_permission_query_conditions",
	"User": "stylo.core.doctype.user.user.get_permission_query_conditions",
	"Dashboard Settings": "stylo.desk.doctype.dashboard_settings.dashboard_settings.get_permission_query_conditions",
	"Notification Log": "stylo.desk.doctype.notification_log.notification_log.get_permission_query_conditions",
	"Dashboard": "stylo.desk.doctype.dashboard.dashboard.get_permission_query_conditions",
	"Dashboard Chart": "stylo.desk.doctype.dashboard_chart.dashboard_chart.get_permission_query_conditions",
	"Number Card": "stylo.desk.doctype.number_card.number_card.get_permission_query_conditions",
	"Notification Settings": "stylo.desk.doctype.notification_settings.notification_settings.get_permission_query_conditions",
	"Note": "stylo.desk.doctype.note.note.get_permission_query_conditions",
	"Kanban Board": "stylo.desk.doctype.kanban_board.kanban_board.get_permission_query_conditions",
	"Contact": "stylo.contacts.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "stylo.contacts.address_and_contact.get_permission_query_conditions_for_address",
	"Communication": "stylo.core.doctype.communication.communication.get_permission_query_conditions_for_communication",
	"Workflow Action": "stylo.workflow.doctype.workflow_action.workflow_action.get_permission_query_conditions",
	"Prepared Report": "stylo.core.doctype.prepared_report.prepared_report.get_permission_query_condition",
	"File": "stylo.core.doctype.file.file.get_permission_query_conditions",
}

has_permission = {
	"Event": "stylo.desk.doctype.event.event.has_permission",
	"ToDo": "stylo.desk.doctype.todo.todo.has_permission",
	"User": "stylo.core.doctype.user.user.has_permission",
	"Note": "stylo.desk.doctype.note.note.has_permission",
	"Dashboard Chart": "stylo.desk.doctype.dashboard_chart.dashboard_chart.has_permission",
	"Number Card": "stylo.desk.doctype.number_card.number_card.has_permission",
	"Kanban Board": "stylo.desk.doctype.kanban_board.kanban_board.has_permission",
	"Contact": "stylo.contacts.address_and_contact.has_permission",
	"Address": "stylo.contacts.address_and_contact.has_permission",
	"Communication": "stylo.core.doctype.communication.communication.has_permission",
	"Workflow Action": "stylo.workflow.doctype.workflow_action.workflow_action.has_permission",
	"File": "stylo.core.doctype.file.file.has_permission",
	"Prepared Report": "stylo.core.doctype.prepared_report.prepared_report.has_permission",
}

has_website_permission = {"Address": "stylo.contacts.doctype.address.address.has_website_permission"}

jinja = {
	"methods": "stylo.utils.jinja_globals",
	"filters": [
		"stylo.utils.data.global_date_format",
		"stylo.utils.markdown",
		"stylo.website.utils.get_shade",
		"stylo.website.utils.abs_url",
	],
}

standard_queries = {"User": "stylo.core.doctype.user.user.user_query"}

doc_events = {
	"*": {
		"after_insert": ["stylo.event_streaming.doctype.event_update_log.event_update_log.notify_consumers"],
		"on_update": [
			"stylo.desk.notifications.clear_doctype_notifications",
			"stylo.core.doctype.activity_log.feed.update_feed",
			"stylo.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"stylo.core.doctype.file.utils.attach_files_to_document",
			"stylo.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
			"stylo.automation.doctype.assignment_rule.assignment_rule.apply",
			"stylo.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"stylo.core.doctype.user_type.user_type.apply_permissions_for_non_standard_user_type",
		],
		"after_rename": "stylo.desk.notifications.clear_doctype_notifications",
		"on_cancel": [
			"stylo.desk.notifications.clear_doctype_notifications",
			"stylo.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"stylo.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
			"stylo.automation.doctype.assignment_rule.assignment_rule.apply",
		],
		"on_trash": [
			"stylo.desk.notifications.clear_doctype_notifications",
			"stylo.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"stylo.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
		],
		"on_update_after_submit": [
			"stylo.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"stylo.automation.doctype.assignment_rule.assignment_rule.apply",
			"stylo.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"stylo.core.doctype.file.utils.attach_files_to_document",
		],
		"on_change": [
			"stylo.social.doctype.energy_point_rule.energy_point_rule.process_energy_points",
			"stylo.automation.doctype.milestone_tracker.milestone_tracker.evaluate_milestone",
		],
	},
	"Event": {
		"after_insert": "stylo.integrations.doctype.google_calendar.google_calendar.insert_event_in_google_calendar",
		"on_update": "stylo.integrations.doctype.google_calendar.google_calendar.update_event_in_google_calendar",
		"on_trash": "stylo.integrations.doctype.google_calendar.google_calendar.delete_event_from_google_calendar",
	},
	"Contact": {
		"after_insert": "stylo.integrations.doctype.google_contacts.google_contacts.insert_contacts_to_google_contacts",
		"on_update": "stylo.integrations.doctype.google_contacts.google_contacts.update_contacts_to_google_contacts",
	},
	"DocType": {
		"on_update": "stylo.cache_manager.build_domain_restriced_doctype_cache",
	},
	"Page": {
		"on_update": "stylo.cache_manager.build_domain_restriced_page_cache",
	},
}

scheduler_events = {
	"cron": {
		"0/15 * * * *": [
			"stylo.oauth.delete_oauth2_data",
			"stylo.website.doctype.web_page.web_page.check_publish_status",
			"stylo.twofactor.delete_all_barcodes_for_users",
		],
		"0/10 * * * *": [
			"stylo.email.doctype.email_account.email_account.pull",
		],
		# Hourly but offset by 30 minutes
		# "30 * * * *": [
		#
		# ],
		# Daily but offset by 45 minutes
		"45 0 * * *": [
			"stylo.core.doctype.log_settings.log_settings.run_log_clean_up",
		],
	},
	"all": [
		"stylo.email.queue.flush",
		"stylo.email.doctype.email_account.email_account.notify_unreplied",
		"stylo.utils.global_search.sync_global_search",
		"stylo.email.queue.retry_sending_emails",
		"stylo.monitor.flush",
	],
	"hourly": [
		"stylo.model.utils.link_count.update_link_count",
		"stylo.model.utils.user_settings.sync_user_settings",
		"stylo.utils.error.collect_error_snapshots",
		"stylo.desk.page.backups.backups.delete_downloadable_backups",
		"stylo.deferred_insert.save_to_db",
		"stylo.desk.form.document_follow.send_hourly_updates",
		"stylo.integrations.doctype.google_calendar.google_calendar.sync",
		"stylo.email.doctype.newsletter.newsletter.send_scheduled_email",
		"stylo.website.doctype.personal_data_deletion_request.personal_data_deletion_request.process_data_deletion_request",
		"stylo.desk.utils.delete_old_exported_report_files",
	],
	"daily": [
		"stylo.email.queue.set_expiry_for_email_queue",
		"stylo.desk.notifications.clear_notifications",
		"stylo.desk.doctype.event.event.send_event_digest",
		"stylo.sessions.clear_expired_sessions",
		"stylo.email.doctype.notification.notification.trigger_daily_alerts",
		"stylo.website.doctype.personal_data_deletion_request.personal_data_deletion_request.remove_unverified_record",
		"stylo.desk.form.document_follow.send_daily_updates",
		"stylo.social.doctype.energy_point_settings.energy_point_settings.allocate_review_points",
		"stylo.integrations.doctype.google_contacts.google_contacts.sync",
		"stylo.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry",
		"stylo.automation.doctype.auto_repeat.auto_repeat.set_auto_repeat_as_completed",
		"stylo.email.doctype.unhandled_email.unhandled_email.remove_old_unhandled_emails",
	],
	"daily_long": [
		"stylo.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_daily",
		"stylo.utils.change_log.check_for_update",
		"stylo.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_daily",
		"stylo.email.doctype.auto_email_report.auto_email_report.send_daily",
		"stylo.integrations.doctype.google_drive.google_drive.daily_backup",
	],
	"weekly_long": [
		"stylo.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_weekly",
		"stylo.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_weekly",
		"stylo.desk.form.document_follow.send_weekly_updates",
		"stylo.social.doctype.energy_point_log.energy_point_log.send_weekly_summary",
		"stylo.integrations.doctype.google_drive.google_drive.weekly_backup",
		"stylo.desk.doctype.changelog_feed.changelog_feed.fetch_changelog_feed",
	],
	"monthly": [
		"stylo.email.doctype.auto_email_report.auto_email_report.send_monthly",
		"stylo.social.doctype.energy_point_log.energy_point_log.send_monthly_summary",
	],
	"monthly_long": [
		"stylo.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_monthly"
	],
}

get_translated_dict = {
	("doctype", "System Settings"): "stylo.geo.country_info.get_translated_dict",
	("page", "setup-wizard"): "stylo.geo.country_info.get_translated_dict",
}

sounds = [
	{"name": "email", "src": "/assets/stylo/sounds/email.mp3", "volume": 0.1},
	{"name": "submit", "src": "/assets/stylo/sounds/submit.mp3", "volume": 0.1},
	{"name": "cancel", "src": "/assets/stylo/sounds/cancel.mp3", "volume": 0.1},
	{"name": "delete", "src": "/assets/stylo/sounds/delete.mp3", "volume": 0.05},
	{"name": "click", "src": "/assets/stylo/sounds/click.mp3", "volume": 0.05},
	{"name": "error", "src": "/assets/stylo/sounds/error.mp3", "volume": 0.1},
	{"name": "alert", "src": "/assets/stylo/sounds/alert.mp3", "volume": 0.2},
	# {"name": "chime", "src": "/assets/stylo/sounds/chime.mp3"},
]

setup_wizard_exception = [
	"stylo.desk.page.setup_wizard.setup_wizard.email_setup_wizard_exception",
	"stylo.desk.page.setup_wizard.setup_wizard.log_setup_wizard_exception",
]

before_migrate = ["stylo.core.doctype.patch_log.patch_log.before_migrate"]
after_migrate = ["stylo.website.doctype.website_theme.website_theme.after_migrate"]

otp_methods = ["OTP App", "Email", "SMS"]

user_data_fields = [
	{"doctype": "Access Log", "strict": True},
	{"doctype": "Activity Log", "strict": True},
	{"doctype": "Comment", "strict": True},
	{
		"doctype": "Contact",
		"filter_by": "email_id",
		"redact_fields": ["first_name", "last_name", "phone", "mobile_no"],
		"rename": True,
	},
	{"doctype": "Contact Email", "filter_by": "email_id"},
	{
		"doctype": "Address",
		"filter_by": "email_id",
		"redact_fields": [
			"address_title",
			"address_line1",
			"address_line2",
			"city",
			"county",
			"state",
			"pincode",
			"phone",
			"fax",
		],
	},
	{
		"doctype": "Communication",
		"filter_by": "sender",
		"redact_fields": ["sender_full_name", "phone_no", "content"],
	},
	{"doctype": "Communication", "filter_by": "recipients"},
	{"doctype": "Email Group Member", "filter_by": "email"},
	{"doctype": "Email Unsubscribe", "filter_by": "email", "partial": True},
	{"doctype": "Email Queue", "filter_by": "sender"},
	{"doctype": "Email Queue Recipient", "filter_by": "recipient"},
	{
		"doctype": "File",
		"filter_by": "attached_to_name",
		"redact_fields": ["file_name", "file_url"],
	},
	{
		"doctype": "User",
		"filter_by": "name",
		"redact_fields": [
			"email",
			"username",
			"first_name",
			"middle_name",
			"last_name",
			"full_name",
			"birth_date",
			"user_image",
			"phone",
			"mobile_no",
			"location",
			"banner_image",
			"interest",
			"bio",
			"email_signature",
		],
	},
	{"doctype": "Version", "strict": True},
]

global_search_doctypes = {
	"Default": [
		{"doctype": "Contact"},
		{"doctype": "Address"},
		{"doctype": "ToDo"},
		{"doctype": "Note"},
		{"doctype": "Event"},
		{"doctype": "Blog Post"},
		{"doctype": "Dashboard"},
		{"doctype": "Country"},
		{"doctype": "Currency"},
		{"doctype": "Newsletter"},
		{"doctype": "Letter Head"},
		{"doctype": "Workflow"},
		{"doctype": "Web Page"},
		{"doctype": "Web Form"},
	]
}

override_whitelisted_methods = {
	# Legacy File APIs
	"stylo.core.doctype.file.file.download_file": "download_file",
	"stylo.core.doctype.file.file.unzip_file": "stylo.core.api.file.unzip_file",
	"stylo.core.doctype.file.file.get_attached_images": "stylo.core.api.file.get_attached_images",
	"stylo.core.doctype.file.file.get_files_in_folder": "stylo.core.api.file.get_files_in_folder",
	"stylo.core.doctype.file.file.get_files_by_search_text": "stylo.core.api.file.get_files_by_search_text",
	"stylo.core.doctype.file.file.get_max_file_size": "stylo.core.api.file.get_max_file_size",
	"stylo.core.doctype.file.file.create_new_folder": "stylo.core.api.file.create_new_folder",
	"stylo.core.doctype.file.file.move_file": "stylo.core.api.file.move_file",
	"stylo.core.doctype.file.file.zip_files": "stylo.core.api.file.zip_files",
	# Legacy (& Consistency) OAuth2 APIs
	"stylo.www.login.login_via_google": "stylo.integrations.oauth2_logins.login_via_google",
	"stylo.www.login.login_via_github": "stylo.integrations.oauth2_logins.login_via_github",
	"stylo.www.login.login_via_facebook": "stylo.integrations.oauth2_logins.login_via_facebook",
	"stylo.www.login.login_via_stylo": "stylo.integrations.oauth2_logins.login_via_stylo",
	"stylo.www.login.login_via_office365": "stylo.integrations.oauth2_logins.login_via_office365",
	"stylo.www.login.login_via_salesforce": "stylo.integrations.oauth2_logins.login_via_salesforce",
	"stylo.www.login.login_via_fairlogin": "stylo.integrations.oauth2_logins.login_via_fairlogin",
}

ignore_links_on_delete = [
	"Communication",
	"ToDo",
	"DocShare",
	"Email Unsubscribe",
	"Activity Log",
	"File",
	"Version",
	"Document Follow",
	"Comment",
	"View Log",
	"Tag Link",
	"Notification Log",
	"Email Queue",
	"Document Share Key",
	"Integration Request",
	"Unhandled Email",
	"Webhook Request Log",
	"Workspace",
	"Route History",
	"Access Log",
]

# Request Hooks
before_request = [
	"stylo.recorder.record",
	"stylo.monitor.start",
	"stylo.rate_limiter.apply",
]
after_request = ["stylo.rate_limiter.update", "stylo.monitor.stop", "stylo.recorder.dump"]

# Background Job Hooks
before_job = [
	"stylo.monitor.start",
]
after_job = [
	"stylo.monitor.stop",
	"stylo.utils.file_lock.release_document_locks",
]

extend_bootinfo = [
	"stylo.utils.telemetry.add_bootinfo",
	"stylo.core.doctype.user_permission.user_permission.send_user_permissions",
]

get_changelog_feed = "stylo.desk.doctype.changelog_feed.changelog_feed.get_feed"
