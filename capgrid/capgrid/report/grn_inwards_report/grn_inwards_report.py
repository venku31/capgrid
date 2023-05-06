# // Copyright (c) 2023, Capgrid Solutions and contributors
# // For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{
			"label": _("GRN"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "GRN Inward",
			"width": 100,
		},
		{"label": _("GRN Date"), "fieldname": "grn_date", "fieldtype": "Date", "width": 100},
		{"fieldname": "grn_time", "label": _("Time"), "fieldtype": "Time", "width": 80},
		{
			"fieldname": "supplier",
			"label": _("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150,
		},
		{
			"label": _("Supplier Name"),
			"fieldname": "supplier_name",
			"fieldtype": "Data",
			"width": 120,
		},
		{"label": _("Supplier Bill No"), "fieldname": "supplier_invoice_no", "fieldtype": "Data", "width": 80},
		{"label": _("Bill Date"), "fieldname": "supplier_invoice_date", "fieldtype": "Data", "width": 80},
		{"label": _("Purchase Receipt"), "fieldname": "purchase_receipt", "fieldtype": "Link","options": "Purchase Receipt", "width": 120},
		{"label": _("Part Number"), "fieldname": "part_number", "fieldtype": "Link", "options": "Item","width": 120},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Parent Lot"),
			"fieldname": "lot_no",
			"fieldtype": "Link",
			"options": "Lot Number",
			"width": 100,
		},
		{"fieldname": "batch_no", "label": _("Lot No"), "fieldtype": "Link", "options": "Lot Number","width": 120},
		{"fieldname": "qty", "label": _("Qty"), "fieldtype": "Float", "width": 100},
		{"fieldname": "purchase_order", "label": _("Purchase Order"), "fieldtype": "Link", "options": "Purchase Order","width": 150},
		
	]
	return columns


def get_data(filters):
	return frappe.db.sql(
		"""
		Select grn.name,
        grn.grn_date,
        grn.grn_time,
        grn.supplier,
        grn.supplier_name,
        grn.supplier_invoice_no,
        grn.supplier_invoice_date,
        grn.purchase_receipt,
        det.part_number,
        det.item_name,
        det.lot_no ,
        det.batch_no,
        det.qty,grn.purchase_order 
        from `tabGRN Inward` grn join `tabGRN Inward Item Details` det ON(grn.name=det.parent and grn.docstatus=1)
		WHERE
			company = %(company)s
			AND DATE(grn.grn_date) BETWEEN %(from_date)s AND %(to_date)s
			{conditions}
		ORDER BY
			grn.grn_date asc """.format(
			conditions=get_conditions(filters)
		),
		filters,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = []

	if filters.get("supplier"):
		conditions.append(" and grn.supplier=%(supplier)s")

	if filters.get("lot_number"):
		conditions.append(" and det.lot_no =%(lot_number)s")

	if filters.get("purchase_order"):
		conditions.append(" and grn.purchase_order =%(purchase_order)s")

	return " ".join(conditions) if conditions else ""