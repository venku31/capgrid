import frappe
from frappe import _, msgprint, scrub
from frappe.model.utils import get_fetch_values
from frappe.utils import (
	add_days,
	add_months,
	add_years,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_last_day,
	get_timestamp,
	getdate,
	nowdate,
)
from six import iteritems

import erpnext
from erpnext import get_company_currency
from erpnext.accounts.utils import get_fiscal_year
from erpnext.exceptions import InvalidAccountCurrency, PartyDisabled, PartyFrozen
from erpnext.accounts.party import get_payment_terms_template

@frappe.whitelist()
def get_due_date(posting_date, party_type, party, company=None, bill_date=None):
	"""Get due date from `Payment Terms Template`"""
	due_date = None
	if (posting_date) and party:
		due_date = posting_date or bill_date
		template_name = get_payment_terms_template(party, party_type, company)

		if template_name:
			due_date = get_due_date_from_template(template_name, posting_date).strftime(
				"%Y-%m-%d"
			)
		else:
			if party_type == "Supplier":
				supplier_group = frappe.get_cached_value(party_type, party, "supplier_group")
				template_name = frappe.get_cached_value("Supplier Group", supplier_group, "payment_terms")
				if template_name:
					due_date = get_due_date_from_template(template_name, posting_date).strftime(
						"%Y-%m-%d"
					)
	# If due date is calculated from bill_date, check this condition
	if getdate(due_date) < getdate(posting_date):
		due_date = posting_date
	return due_date


def get_due_date_from_template(template_name, posting_date):
	"""
	Inspects all `Payment Term`s from the a `Payment Terms Template` and returns the due
	date after considering all the `Payment Term`s requirements.
	:param template_name: Name of the `Payment Terms Template`
	:return: String representing the calculated due date
	"""
	due_date = getdate(posting_date)

	template = frappe.get_doc("Payment Terms Template", template_name)

	for term in template.terms:
		if term.due_date_based_on == "Day(s) after invoice date":
			due_date = max(due_date, add_days(due_date, term.credit_days))
		elif term.due_date_based_on == "Day(s) after the end of the invoice month":
			due_date = max(due_date, add_days(get_last_day(due_date), term.credit_days))
		else:
			due_date = max(due_date, add_months(get_last_day(due_date), term.credit_months))
	return due_date


def validate_due_date(
	posting_date, due_date, party_type, party, company=None, bill_date=None, template_name=None
):
	if getdate(due_date) < getdate(posting_date):
		frappe.throw(_("Due Date cannot be before Posting / Supplier Invoice Date"))
	else:
		if not template_name:
			return

		default_due_date = get_due_date_from_template(template_name, posting_date, bill_date).strftime(
			"%Y-%m-%d"
		)

		if not default_due_date:
			return

		if default_due_date != posting_date and getdate(due_date) > getdate(default_due_date):
			is_credit_controller = (
				frappe.db.get_single_value("Accounts Settings", "credit_controller") in frappe.get_roles()
			)
			if is_credit_controller:
				msgprint(
					_("Note: Due / Reference Date exceeds allowed customer credit days by {0} day(s)").format(
						date_diff(due_date, default_due_date)
					)
				)
			else:
				frappe.throw(
					_("Due / Reference Date cannot be after {0}").format(formatdate(default_due_date))
				)