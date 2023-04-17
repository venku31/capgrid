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
def search_lot(batch):
    # item_data = search_serial_or_batch_or_barcode_number(batch)
    # if item_data != 0:
    # main_lot = frappe.db.sql("""SELECT parent_lot from `tabLot Number` where name='%(batch)s' """%{"batch": batch}, as_dict = 1)
    main_lot = frappe.db.get_value("GRN Inward Item Details", {"batch_no": batch}, "lot_no")
    print("////////////",main_lot)
    if main_lot :
        stock = frappe.db.sql("""SELECT iw.name as grn,iw.purchase_order,iw.purchase_receipt,iwd.part_number,iwd.item_name,iwd.packet,iwd.qty,iwd.batch_no,iwd.lot_no,iw.supplier,iw.supplier_name,iw.supplier_invoice_no,iw.supplier_invoice_date,iw.owner
	    from `tabGRN Inward` iw LEFT JOIN `tabGRN Inward Item Details` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 and iwd.lot_no = '%(batch)s' """%{"batch": main_lot}, as_dict = 1)
        return stock
    else :
        stock = frappe.db.sql("""SELECT iw.name as grn,iw.purchase_order,iw.purchase_receipt,iwd.part_number,iwd.item_name,iwd.packet,iwd.qty,iwd.batch_no,iwd.lot_no,iw.supplier,iw.supplier_name,iw.supplier_invoice_no,iw.supplier_invoice_date,iw.owner
	    from `tabGRN Inward` iw LEFT JOIN `tabGRN Inward Item Details` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 and iwd.lot_no = '%(batch)s' """%{"batch": batch}, as_dict = 1)
        return stock
    
def create_quality_inspection(doc, handler=""):
    # for item in doc.quality_inspection_page_table:
    qi = frappe.new_doc("Quality Inspection")
    part_number=frappe.db.get_value("GRN Inward Item",{"parent":doc.grn},'part_number')
    lot_no=frappe.db.get_value("GRN Inward Item",{"parent":doc.grn},'lot_no')
    qi.update({ "inspection_type": "Incoming" , "reference_type": "Purchase Receipt","reference_name": doc.purchase_receipt,"status":"Accepted","item_code":part_number,"lot_number":lot_no,"sample_size":doc.total_inward_qty,"inspected_by":doc.owner})
        
    qi.docstatus=1
    qi.insert()
    update_main_lot(doc)
    update_lot(doc)

def update_lot(doc):
    for row in doc.quality_inspection_page_table:
        if row.batch_no :
            lot = frappe.get_doc('Lot Number', row.batch_no)
   
            lot.quality_inspection_page = doc.name
            lot.accepted_qty = row.accepted_qty
            lot.rejected_qty = row.rejected_qty
            lot.purchase_receipt = doc.purchase_receipt
            lot.created_by = doc.created_by
            lot.save(ignore_permissions=True)
            frappe.db.commit()
def update_main_lot(doc):
    lot_no=frappe.db.get_value("GRN Inward Item",{"parent":doc.grn},'lot_no')
    if lot_no :
        lot = frappe.get_doc('Lot Number',lot_no)
        lot.quality_inspection_page = doc.name
        lot.accepted_qty = doc.total_accepted_qty
        lot.rejected_qty = doc.total_rejected_qty
        lot.purchase_receipt = doc.purchase_receipt
        lot.created_by = doc.created_by
        lot.save(ignore_permissions=True)
        frappe.db.commit()
 