import frappe
from frappe.model.mapper import get_mapped_doc
from erpnext.controllers.accounts_controller import get_payment_terms
from frappe.utils import (
	add_days,
	add_months,
	cint,
	flt,
	fmt_money,
	formatdate,
	get_last_day,
	get_link_to_form,
	getdate,
	nowdate,
	today,
)
from erpnext.accounts.party import (
	get_party_account,
	get_party_account_currency,
	get_party_gle_currency,
	validate_party_frozen_disabled,
)
from six import text_type

@frappe.whitelist()
def validate_due_date(self):
    if self.get("is_pos"):
        return

    from erpnext.accounts.party import validate_due_date

    if self.doctype == "Sales Invoice":
        if not self.due_date:
            frappe.throw(_("Due Date is mandatory"))

        validate_due_date(
            self.posting_date,
            self.due_date,
            "Customer",
            self.customer,
            self.company,
            self.payment_terms_template,
        )
    elif self.doctype == "Purchase Invoice":
        validate_due_date(
            self.posting_date or self.bill_date,
            self.due_date,
            "Supplier",
            self.supplier,
            self.company,
            self.posting_date,
            self.payment_terms_template,
        )

@frappe.whitelist()
def get_payment_terms(
	terms_template, posting_date=None, grand_total=None, base_grand_total=None, bill_date=None
):
	if not terms_template:
		return

	terms_doc = frappe.get_doc("Payment Terms Template", terms_template)

	schedule = []
	for d in terms_doc.get("terms"):
		term_details = get_payment_term_details(
			d, posting_date, grand_total, base_grand_total, posting_date
		)
		schedule.append(term_details)

	return schedule

@frappe.whitelist()
def get_payment_term_details(
	term, posting_date=None, grand_total=None, base_grand_total=None, bill_date=None
):
	term_details = frappe._dict()
	if isinstance(term, text_type):
		term = frappe.get_doc("Payment Term", term)
	else:
		term_details.payment_term = term.payment_term
	term_details.description = term.description
	term_details.invoice_portion = term.invoice_portion
	term_details.payment_amount = flt(term.invoice_portion) * flt(grand_total) / 100
	term_details.base_payment_amount = flt(term.invoice_portion) * flt(base_grand_total) / 100
	term_details.discount_type = term.discount_type
	term_details.discount = term.discount
	term_details.outstanding = term_details.payment_amount
	term_details.mode_of_payment = term.mode_of_payment

	if bill_date:
		term_details.due_date = get_due_date(term, posting_date)
		term_details.discount_date = get_discount_date(term, posting_date)
	elif posting_date:
		term_details.due_date = get_due_date(term, posting_date)
		term_details.discount_date = get_discount_date(term, posting_date)

	if getdate(term_details.due_date) < getdate(posting_date):
		term_details.due_date = posting_date

	return term_details

@frappe.whitelist()
def get_due_date(term, posting_date=None, bill_date=None):
    due_date = None
    date = posting_date or bill_date
    if term.due_date_based_on == "Day(s) after invoice date":
        due_date = add_days(date, term.credit_days)
    elif term.due_date_based_on == "Day(s) after the end of the invoice month":
        due_date = add_days(get_last_day(date), term.credit_days)
    elif term.due_date_based_on == "Month(s) after the end of the invoice month":
        due_date = add_months(get_last_day(date), term.credit_months)
    return due_date

@frappe.whitelist()
def set_payment_schedule(self):
		if self.doctype == "Sales Invoice" and self.is_pos:
			self.payment_terms_template = ""
			return

		party_account_currency = self.get("party_account_currency")
		if not party_account_currency:
			party_type, party = self.get_party()

			if party_type and party:
				party_account_currency = get_party_account_currency(party_type, party, self.company)

		posting_date = self.get("posting_date") or self.get("bill_date") or self.get("transaction_date")
		date = self.get("due_date")
		due_date = posting_date or date

		base_grand_total = self.get("base_rounded_total") or self.base_grand_total
		grand_total = self.get("rounded_total") or self.grand_total

		if self.doctype in ("Sales Invoice", "Purchase Invoice"):
			base_grand_total = base_grand_total - flt(self.base_write_off_amount)
			grand_total = grand_total - flt(self.write_off_amount)
			po_or_so, doctype, fieldname = self.get_order_details()
			automatically_fetch_payment_terms = cint(
				frappe.db.get_single_value("Accounts Settings", "automatically_fetch_payment_terms")
			)

		if self.get("total_advance"):
			if party_account_currency == self.company_currency:
				base_grand_total -= self.get("total_advance")
				grand_total = flt(
					base_grand_total / self.get("conversion_rate"), self.precision("grand_total")
				)
			else:
				grand_total -= self.get("total_advance")
				base_grand_total = flt(
					grand_total * self.get("conversion_rate"), self.precision("base_grand_total")
				)

		if not self.get("payment_schedule"):
			if (
				self.doctype in ["Sales Invoice", "Purchase Invoice"]
				and automatically_fetch_payment_terms
				and self.linked_order_has_payment_terms(po_or_so, fieldname, doctype)
			):
				self.fetch_payment_terms_from_order(po_or_so, doctype)
				if self.get("payment_terms_template"):
					self.ignore_default_payment_terms_template = 1
			elif self.get("payment_terms_template"):
				data = get_payment_terms(
					self.payment_terms_template, posting_date, grand_total, base_grand_total
				)
				for item in data:
					self.append("payment_schedule", item)
			elif self.doctype not in ["Purchase Receipt"]:
				data = dict(
					due_date=due_date,
					invoice_portion=100,
					payment_amount=grand_total,
					base_payment_amount=base_grand_total,
				)
				self.append("payment_schedule", data)

		for d in self.get("payment_schedule"):
			if d.invoice_portion:
				d.payment_amount = flt(
					grand_total * flt(d.invoice_portion / 100), d.precision("payment_amount")
				)
				d.base_payment_amount = flt(
					base_grand_total * flt(d.invoice_portion / 100), d.precision("base_payment_amount")
				)
				d.outstanding = d.payment_amount
			elif not d.invoice_portion:
				d.base_payment_amount = flt(
					d.payment_amount * self.get("conversion_rate"), d.precision("base_payment_amount")
				)
def get_discount_date(term, posting_date=None, bill_date=None):
	discount_validity = None
	date = posting_date or bill_date
	if term.discount_validity_based_on == "Day(s) after invoice date":
		discount_validity = add_days(date, term.discount_validity)
	elif term.discount_validity_based_on == "Day(s) after the end of the invoice month":
		discount_validity = add_days(get_last_day(date), term.discount_validity)
	elif term.discount_validity_based_on == "Month(s) after the end of the invoice month":
		discount_validity = add_months(get_last_day(date), term.discount_validity)
	return discount_validity