# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data
import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{
			"fieldname": "invoice_no",
			"label": _("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "date",
			"width": 100,
		},
		{
			"label": _("Invoice Amount"),
			"fieldname": "invoice_total",
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"label": _("GL Amount"),
			"fieldname": "gl_amount",
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "difference",
			"label": _("Difference"),
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "data",
			"width": 150,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "data",
			"width": 100,
		},
			
	]
	return columns


def get_data(filters):
	return frappe.db.sql(
		"""
		Select invoice_no,posting_date,invoice_total,gl_amount,(invoice_total-gl_amount) as difference,company,customer
		from
		(Select gl.voucher_no as invoice_no,party as customer,
		gl.posting_date,
		case (select rounded_total from `tabSales Invoice` where name=gl.voucher_no)
		when 0 then (select grand_total from `tabSales Invoice` where name=gl.voucher_no)
		else (select rounded_total from `tabSales Invoice` where name=gl.voucher_no)
		end as invoice_total,
		gl.debit_in_account_currency as gl_amount,
		0 as difference,gl.company,gl.party_type,gl.is_cancelled,gl.credit,gl.against_voucher_type
		from `tabGL Entry` gl where gl.is_cancelled=0 and gl.credit=0
		UNION
		Select gl.voucher_no as invoice_no,party as customer,
		gl.posting_date,
		case (select rounded_total from `tabSales Invoice` where name=gl.voucher_no)
		when 0 then -(select grand_total from `tabSales Invoice` where name=gl.voucher_no)
		else -(select rounded_total from `tabSales Invoice` where name=gl.voucher_no)
		end as invoice_total,
		gl.credit_in_account_currency as gl_amount,
		0 as difference,gl.company,gl.party_type,gl.is_cancelled,gl.credit,gl.against_voucher_type
		from `tabGL Entry` gl where gl.is_cancelled=0 and gl.debit=0
		)gl
		where gl.against_voucher_type="Sales Invoice" and gl.party_type="Customer"
 AND DATE(gl.posting_date) BETWEEN %(from_date)s AND %(to_date)s and (invoice_total-gl_amount)<>'0'
  {conditions}
ORDER BY
			gl.posting_date ,gl.invoice_no """.format(
			conditions=get_conditions(filters)
		),
		filters,
		as_dict=1,
	)
	

def get_conditions(filters):
	conditions = []

	if filters.get("customer"):
		conditions.append(" and gl.customer=%(customer)s")
	
	return " ".join(conditions) if conditions else ""