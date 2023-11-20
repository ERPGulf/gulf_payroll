app_name = "gulf_payroll"
app_title = "Gulf Payroll"
app_publisher = "ERPGulf"
app_description = "App to calculate Leave encashment and gratuity in the Gulf countries"
app_email = "support@ERPGulf.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gulf_payroll/css/gulf_payroll.css"
# app_include_js = "/assets/gulf_payroll/js/gulf_payroll.js"

# include js, css files in header of web template
# web_include_css = "/assets/gulf_payroll/css/gulf_payroll.css"
# web_include_js = "/assets/gulf_payroll/js/gulf_payroll.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "gulf_payroll/public/scss/website"

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

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "gulf_payroll/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "gulf_payroll.utils.jinja_methods",
#	"filters": "gulf_payroll.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "gulf_payroll.install.before_install"
# after_install = "gulf_payroll.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "gulf_payroll.uninstall.before_uninstall"
# after_uninstall = "gulf_payroll.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "gulf_payroll.utils.before_app_install"
# after_app_install = "gulf_payroll.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "gulf_payroll.utils.before_app_uninstall"
# after_app_uninstall = "gulf_payroll.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "gulf_payroll.notifications.get_notification_config"

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

# override_doctype_class = {
# 	"Leave Encashment": "gulf_payroll.gulf_payroll.Leave Encashment.LeaveEncashment_new"
# }

override_doctype_class = {
	"Gratuity": "gulf_payroll.gulf_payroll.gratuity_new.Gratuity_new",
    "Leave Encashment": "gulf_payroll.gulf_payroll.Leave Encashment_new.LeaveEncashment_new"
}

override_whitelisted_methods = {
    "hrms.payroll.doctype.gratuity.gratuity.calculate_work_experience_and_amount": "gulf_payroll.gulf_payroll.gratuity_new.calculate_work_experience_and_amount",
   
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"gulf_payroll.tasks.all"
#	],
#	"daily": [
#		"gulf_payroll.tasks.daily"
#	],
#	"hourly": [
#		"gulf_payroll.tasks.hourly"
#	],
#	"weekly": [
#		"gulf_payroll.tasks.weekly"
#	],
#	"monthly": [
#		"gulf_payroll.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "gulf_payroll.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "gulf_payroll.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "gulf_payroll.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["gulf_payroll.utils.before_request"]
# after_request = ["gulf_payroll.utils.after_request"]

# Job Events
# ----------
# before_job = ["gulf_payroll.utils.before_job"]
# after_job = ["gulf_payroll.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"gulf_payroll.auth.validate"
# ]

fixtures=[{ "dt":"Property Setter" ,"filters":[[
                "name", "in",[
                    "Leave Allocation-to_date-default","Leave Allocation-from_date-fetch_from"] ]] 
           }]
fixtures = [ {"dt": "Custom Field","filters": [["module", "=", "Gulf Payroll"]] }]