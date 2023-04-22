# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

# import frappe
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
class Putaway(Document):
	pass

@frappe.whitelist()
def search_lot(batch):
    # main_lot = frappe.db.get_value("Quality Inspection Page Table", {"batch_no": batch}, "lot_no")
    # print("////////////",main_lot)
    # if main_lot :
    #     stock = frappe.db.sql("""SELECT iw.name as grn,iwd.part_number,iwd.description,iwd.qty,iwd.batch_no,iwd.lot_no,iw.owner,(select location from `tabItem` where name=iwd.part_number) as location
	#     from `tabQuality Inspection Page` iw LEFT JOIN `tabQuality Inspection Page Table` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 and iwd.lot_no = '%(batch)s' """%{"batch": main_lot}, as_dict = 1)
    #     return stock
    # else :
    stock = frappe.db.sql("""SELECT iw.name as grn,iwd.part_number,iwd.description,iwd.qty,iwd.batch_no,iwd.lot_no,iw.owner,(select location from `tabItem` where name=iwd.part_number) as location
	from `tabQuality Inspection Page` iw LEFT JOIN `tabQuality Inspection Page Table` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 and iwd.batch_no = '%(batch)s' """%{"batch": batch}, as_dict = 1)
    return stock
# def create_quality_inspection(doc, handler=""):
#     for item in doc.quality_inspection_page_table:
#         qi = frappe.new_doc("Quality Inspection")
#         qi.update({ "inspection_type": "Incoming" , "reference_type": "Purchase Receipt","reference_name": item.purchase_receipt,"status":item.status,"item_code":item.part_number,"lot_number":item.batch_no,"sample_size":item.qty,"inspected_by":doc.owner})
        
#         qi.docstatus=1
#         qi.insert()
