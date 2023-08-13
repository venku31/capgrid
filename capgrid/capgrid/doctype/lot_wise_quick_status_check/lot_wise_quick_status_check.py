# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LotwiseQuickStatusCheck(Document):
	pass

@frappe.whitelist()
def scan_lot(lot_no):
    stock = frappe.db.sql("""SELECT            
        sle.lot_number,sle.item_code,sle.stock_uom,sle.warehouse_location,sle.warehouse,sle.actual_qty
        FROM `tabStock Ledger Entry` sle
        where (sle.docstatus < 2) and (sle.is_cancelled = 0) and sle.lot_number ='%(lot_no)s' and sle.actual_qty>0
        order by creation desc  LIMIT 1
    """%{"lot_no": lot_no}, as_dict = 1)
    return stock