from . import __version__ as app_version

app_name = "capgrid"
app_title = "Capgrid"
app_publisher = "Capgrid Solutions"
app_description = "ERPNext Customisations for Capgrid"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "venkatesh@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/capgrid/css/capgrid.css"
# app_include_js = "/assets/capgrid/js/capgrid.js"

# include js, css files in header of web template
# web_include_css = "/assets/capgrid/css/capgrid.css"
# web_include_js = "/assets/capgrid/js/capgrid.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "capgrid/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "capgrid.install.before_install"
# after_install = "capgrid.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "capgrid.uninstall.before_uninstall"
# after_uninstall = "capgrid.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "capgrid.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
"Inward GRN": {
         "on_update": "capgrid.capgrid.doctype.inward_grn.inward_grn.before_validate",
		#  "after_validate": "capgrid.capgrid.doctype.inward_grn.inward_grn.before_validate",
    },
"Quality Inspection Page": {
		"validate": "capgrid.capgrid.doctype.quality_inspection_page.quality_inspection_page.create_quality_inspection"
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"capgrid.tasks.all"
#	],
#	"daily": [
#		"capgrid.tasks.daily"
#	],
#	"hourly": [
#		"capgrid.tasks.hourly"
#	],
#	"weekly": [
#		"capgrid.tasks.weekly"
#	]
#	"monthly": [
#		"capgrid.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "capgrid.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "capgrid.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "capgrid.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Request Events
# ----------------
# before_request = ["capgrid.utils.before_request"]
# after_request = ["capgrid.utils.after_request"]

# Job Events
# ----------
# before_job = ["capgrid.utils.before_job"]
# after_job = ["capgrid.utils.after_job"]

# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"capgrid.auth.validate"
# ]

from erpnext.controllers.accounts_controller import AccountsController as _AccountsController
from erpnext.accounts import party as _party
# from pos_bahrain.api.taxes_and_totals import calculate_change_amount,calculate_write_off_amount,update_paid_amount_for_return_ov
from capgrid.api.purchase_invoice import get_due_date,validate_due_date,set_payment_schedule,get_payment_term_details,get_payment_terms
from capgrid.api.party import get_due_date
_AccountsController.get_due_date = get_due_date
_AccountsController.validate_due_date = validate_due_date
_AccountsController.set_payment_schedule = set_payment_schedule
_AccountsController.get_payment_term_details = get_payment_term_details
_AccountsController.get_payment_terms = get_payment_terms
_party.get_due_date = get_due_date