# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{
			"label": _("QI"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Quality Inspection Page",
			"width": 100,
		},
		{"label": _("QI Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
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
		{"fieldname": "main_warehouse", "label": _("Main Warehouse"), "fieldtype": "Link", "options": "Warehouse","width": 150},
		{"label": _("Supplier Bill No"), "fieldname": "supplier_invoice_no", "fieldtype": "Data", "width": 80},
		{"label": _("Bill Date"), "fieldname": "supplier_invoice_date", "fieldtype": "Data", "width": 80},
		{"label": _("Purchase Receipt"), "fieldname": "purchase_receipt", "fieldtype": "Link","options": "Purchase Receipt", "width": 120},
		{"fieldname": "purchase_order", "label": _("Purchase Order"), "fieldtype": "Link", "options": "Purchase Order","width": 150},
		
	]
	return columns


def get_data(filters):
	return frappe.db.sql(
		"""
		Select qi.name,
        qi.date,
        qi.supplier,
        qi.supplier_name,
        qi.supplier_invoice_no,
        qi.supplier_invoice_date,
        qi.purchase_receipt,
        det.part_number,
        det.description as item_name,
        det.lot_no ,
        det.batch_no,
        det.qty,qi.purchase_order,qi.main_warehouse 
        from `tabQuality Inspection Page` qi join `tabQuality Inspection Page Table` det ON(qi.name=det.parent and qi.docstatus=1 and qi.date>="2023-09-01")
		WHERE
			company = %(company)s
			AND DATE(qi.date) BETWEEN %(from_date)s AND %(to_date)s
			AND det.batch_no NOT IN (select `tabPutaway`.batch_no from `tabPutaway` 
			where `tabPutaway`.docstatus=1 and `tabPutaway`.batch_no=det.batch_no)
			{conditions}
		ORDER BY
			qi.date,det.batch_no asc """.format(
			conditions=get_conditions(filters)
		),
		filters,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = []

	if filters.get("supplier"):
		conditions.append(" and qi.supplier=%(supplier)s")

	if filters.get("main_warehouse"):
		conditions.append(" and qi.main_warehouse =%(main_warehouse)s")

	if filters.get("purchase_order"):
		conditions.append(" and qi.purchase_order =%(purchase_order)s")

	return " ".join(conditions) if conditions else ""
