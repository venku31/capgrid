# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PickingList(Document):
	pass



@frappe.whitelist()
def get_stock_warehouse_locations(company, warehouse):
	stock = frappe.db.sql(""" SELECT sle.item_code,
            sle.warehouse,
            sle.warehouse_location,
            sle.lot_number,
            sle.posting_date,
            sle.actual_qty
        FROM `tabStock Ledger Entry` sle
        where (sle.docstatus < 2) and (sle.is_cancelled = 0) and sle.warehouse_location !="" and 
		sle.actual_qty>0 and sle.warehouse='%(warehouse)s' and sle.company='%(company)s'  
        order by posting_date desc, posting_time desc, creation desc limit 1 
        """ %{"warehouse": warehouse,"company":company}, as_dict = 1)
	
	return stock