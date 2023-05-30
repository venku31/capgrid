from datetime import date

import frappe
from frappe import _, msgprint
from frappe.query_builder.functions import Sum
from frappe.utils import (
    add_days,
    ceil,
    cint,
    cstr,
    date_diff,
    floor,
    flt,
    formatdate,
    get_first_day,
    get_link_to_form,
    getdate,
    money_in_words,
    rounded,
)
import erpnext
from erpnext.accounts.utils import get_fiscal_year
from erpnext.loan_management.doctype.loan_repayment.loan_repayment import (
    calculate_amounts,
    create_repayment_entry,
)


from hrms.payroll.doctype.additional_salary.additional_salary import get_additional_salaries
from hrms.payroll.doctype.employee_benefit_application.employee_benefit_application import (
    get_benefit_component_amount,
)
from hrms.payroll.doctype.employee_benefit_claim.employee_benefit_claim import (
    get_benefit_claim_amount,
    get_last_payroll_period_benefits,
)
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates
from hrms.payroll.doctype.payroll_period.payroll_period import (
    get_payroll_period,
    get_period_factor,
)

def get_year_to_date_period(self):
	if self.payroll_period:
		period_start_date = self.payroll_period.start_date
		period_end_date = self.payroll_period.end_date
	else:
		# get dates based on fiscal year if no payroll period exists
		fiscal_year = get_fiscal_year(date=self.start_date, company=self.company, as_dict=1)
		period_start_date = fiscal_year.year_start_date
		period_end_date = fiscal_year.year_end_date

	return period_start_date, period_end_date
@frappe.whitelist()
def compute_benifit_claim_year_to_date(doc,method=None):
    year_to_date = 0
    period_start_date, period_end_date = doc.get_year_to_date_period()

    benefit_claim_sum = frappe.get_list(
            "Employee Benefit Claim",
            fields=["sum(claimed_amount) as claimed_amount"],
            filters={
                "employee": doc.employee,
                "claim_date": [">=", period_start_date],
                "claim_date": ["<", period_end_date],
                # "name": ["!=", self.name],
                "docstatus": 1,
            },
    )

    year_to_date = flt(benefit_claim_sum[0].claimed_amount) if benefit_claim_sum else 0.0
    doc.total_fy_benefits_claimed = year_to_date
    doc.gross_pay_year_without_claim_benifit=doc.gross_year_to_date-year_to_date
    compute_month_to_date(doc)

@frappe.whitelist()
def compute_month_to_date(doc,method=None):
    month_to_date = 0
    first_day_of_the_month = get_first_day(doc.start_date)
    end_date = doc.end_date
    claimed_benefit = frappe.get_list(
            "Employee Benefit Claim",
            fields=["sum(claimed_amount) as claimed_amount"],
            filters={
                "employee": doc.employee,
                "claim_date": [">=", first_day_of_the_month],
                "claim_date": ["<=", doc.end_date],
                "docstatus": 1,
            },
        )

    month_to_date = flt(claimed_benefit[0].claimed_amount) if claimed_benefit else 0.0

    # month_to_date += doc.claimed_amount
    doc.claimed_benefits = month_to_date
    doc.gross_pay_without_claim_benifit=doc.gross_pay-month_to_date