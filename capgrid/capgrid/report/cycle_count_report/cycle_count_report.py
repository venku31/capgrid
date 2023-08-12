# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{
			"fieldname": "location",
			"label": _("Location"),
			"fieldtype": "Link",
			"options": "Warehouse Location",
			"width": 120,
		},
		{
			"label": _("Part Number"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 120,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Lot"),
			"fieldname": "lot_number",
			"fieldtype": "Link",
			"options": "Lot Number",
			"width": 120,
		},
			{
			"fieldname": "lot_location",
			"label": _("Lot Location"),
			"fieldtype": "Link",
			"options": "Warehouse Location",
			"width": 120,
		},
				
		{"fieldname": "quantity", "label": _("Qty"), "fieldtype": "Float", "width": 100},
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
		{"label": _("Created By"), "fieldname": "created_by", "fieldtype": "Data", "width": 100},
				
	]
	return columns


def get_data(filters):
	return frappe.db.sql(
		"""
		Select cc.name,
		cc.location,
		cc.company,
		cc.warehouse,
		cc.date,
		cc.created_by,
		ccd.lot_number,
		ccd.item_code,
		ccd.item_name,
		ccd.quantity,
		ccd.location as lot_location from `tabCycle Count` cc join `tabCycle Count Details` ccd ON(cc.name=ccd.parent and cc.docstatus=1) 
		WHERE
			cc.company = %(company)s
			AND DATE(cc.date) BETWEEN %(from_date)s AND %(to_date)s
			{conditions}
		ORDER BY
			cc.date,cc.location asc """.format(
			conditions=get_conditions(filters)
		),
		filters,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = []

	if filters.get("location"):
		conditions.append(" and cc.location=%(location)s")

	if filters.get("main_warehouse"):
		conditions.append(" and cc.warehouse =%(main_warehouse)s")

	
	return " ".join(conditions) if conditions else ""