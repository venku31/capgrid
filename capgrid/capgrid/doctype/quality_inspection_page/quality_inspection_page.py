# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
import json
from frappe.utils import (
    add_days,
    ceil,
    cint,
    comma_and,
    flt,
    get_link_to_form,
    getdate,
    now_datetime,
    nowdate,today,formatdate, get_first_day, get_last_day 
)
from datetime import date,timedelta
from frappe.model.document import Document

class QualityInspectionPage(Document):
	pass

@frappe.whitelist()
def search_batch(batch):
    # item_data = search_serial_or_batch_or_barcode_number(batch)
    # if item_data != 0:
    stock = frappe.db.sql("""SELECT iw.name as grn,iw.purchase_order,iw.purchase_receipt,iwd.part_number,iwd.item_name,iwd.packet,iwd.qty,iwd.batch_no
	from `tabInward GRN` iw LEFT JOIN `tabInward GRN Item Details` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 and iwd.batch_no = '%(batch)s' """%{"batch": batch}, as_dict = 1)
    return stock
    
def create_quality_inspection(doc, handler=""):
    for item in doc.quality_inspection_page_table:
        qi = frappe.new_doc("Quality Inspection")
        qi.update({ "inspection_type": "Incoming" , "reference_type": "Purchase Receipt","reference_name": item.purchase_receipt,"status":item.status,"item_code":item.part_number,"batch_no":item.batch_no,"sample_size":1,"inspected_by":"Administrator"})
        
        qi.docstatus=1
        qi.insert()