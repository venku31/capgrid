# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	columns, final_data = get_actual_qty(data, filters)
	return columns, data

def get_actual_qty(data, filters):
    final_data = []
    company = filters.get("company")

    for row in data:
        item_code = row.get("part_number")  # Assuming "part_number" is equivalent to "item_code"
        parent_warehouse = row.get("main_warehouse")

        # Determine the warehouse containing the substring "Under QC" for the given company
        warehouse = frappe.db.sql(
            """
            SELECT name 
            FROM `tabWarehouse`
            WHERE company = %s
			AND parent_warehouse = %s			
            AND warehouse_name LIKE %s

            LIMIT 1
            """,
            (company,parent_warehouse, "%Under QC%"),
            as_dict=True,
        )[0].get("name")

        # Fetch the sum of actual_qty for the given item_code and dynamically determined warehouse
        actual_qty = frappe.db.sql(
            """
            SELECT SUM(actual_qty) as qty 
            FROM `tabStock Ledger Entry`
            WHERE item_code = %s
            AND warehouse = %s
            AND docstatus = 1
            """,
            (item_code, warehouse),
            as_dict=True,
        )[0].get("qty")

        # Add the actual_qty to the row
        row["actual_qty"] = actual_qty
        final_data.append(row)

    columns = get_columns()
    return columns, final_data

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
		{"fieldname": "actual_qty", "label": _("Actual Qty"), "fieldtype": "Float", "width": 100},		
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
        det.qty,grn.purchase_order,grn.main_warehouse 
        from `tabGRN Inward` grn join `tabGRN Inward Item Details` det ON(grn.name=det.parent and grn.docstatus=1)
		WHERE
			company = %(company)s
			AND DATE(grn.grn_date) BETWEEN %(from_date)s AND %(to_date)s and grn.grn_date>="2023-06-01"
			AND det.batch_no NOT IN (select `tabQuality Inspection Page Table`.batch_no from `tabQuality Inspection Page Table` 
			where `tabQuality Inspection Page Table`.docstatus=1 and `tabQuality Inspection Page Table`.batch_no=det.batch_no)
			AND det.is_stock_item=1
			{conditions}
		ORDER BY
			grn.grn_date,det.batch_no asc """.format(
			conditions=get_conditions(filters)
		),
		filters,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = []

	if filters.get("supplier"):
		conditions.append(" and grn.supplier=%(supplier)s")

	if filters.get("main_warehouse"):
		conditions.append(" and grn.main_warehouse =%(main_warehouse)s")

	if filters.get("purchase_order"):
		conditions.append(" and grn.purchase_order =%(purchase_order)s")

	return " ".join(conditions) if conditions else ""