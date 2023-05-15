# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LocationMovement(Document):
    pass
@frappe.whitelist()
def search_location_mv_lot(lot_number,company):
    # stock = frappe.db.sql("""SELECT iw.name as grn,iwd.part_number,iwd.description,iwd.accepted_qty,iwd.batch_no,iwd.lot_no,iw.owner,(select warehouse_location from `tabItem Default` where parent=iwd.part_number and company='%(company)s') as location
    # from `tabQuality Inspection Page` iw LEFT JOIN `tabQuality Inspection Page Table` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 and iwd.accepted_qty>0
    # and  iwd.batch_no NOT IN (select `tabPutaway`.batch_no from `tabPutaway` where `tabPutaway`.docstatus=1 and `tabPutaway`.batch_no='%(batch)s') and iwd.batch_no = '%(batch)s' """%{"batch": batch,"company":company}, as_dict = 1)
    # return stock
    if lot_number :
        stock = frappe.db.sql(""" SELECT sle.item_code,
            sle.warehouse,
            sle.warehouse_location,
            sle.lot_number,
            sle.posting_date,
            sle.actual_qty
        FROM `tabStock Ledger Entry` sle
        where (sle.docstatus < 2) and (sle.is_cancelled = 0) and sle.warehouse_location !="" and sle.actual_qty>0 and sle.lot_number='%(lot_number)s' 
        order by posting_date desc, posting_time desc, creation desc limit 1 
        """ %{"lot_number": lot_number,"company":company}, as_dict = 1)
        return stock

def create_lm_stock_entry(doc, handler=""):
    # if doc.scaned_location == doc.location :
    se = frappe.new_doc("Stock Entry")
    se.update({ "purpose": "Repack" , "stock_entry_type": "Repack"})
    item_code = doc.part_number
    item_price_rate = frappe.db.get_value('Item Price', {'item_code':doc.part_number,'price_list':"Standard Buying"}, 'price_list_rate')
    se.append("items", { 
    "item_code":doc.part_number,
    "qty": doc.actual_qty,
    "transfer_qty":doc.actual_qty,
    "s_warehouse": doc.from_warehouse,
    "t_warehouse": "",
    "set_basic_rate_manually":1,
    "basic_rate" : item_price_rate or 0,
    "expense_account": frappe.db.get_value("Company", {"name":doc.company}, "default_expense_account"),
    "reference_purchase_receipt":frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "purchase_receipt"),
    "warehouse_location" : doc.part_number_location,
    "lot_number":doc.batch_no,
    "allow_zero_valuation_rate":1,
    "conversion_factor":1,
    "cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
    })
    se.append("items", { 
    "item_code":doc.part_number,
    "qty": doc.actual_qty,
    "transfer_qty":doc.actual_qty,
    "s_warehouse": "",
    "t_warehouse": frappe.db.get_value("Warehouse Location", {"name":doc.scaned_location}, "warehouse"),
    "is_finished_item":1,
    "set_basic_rate_manually":1,
    "basic_rate" : item_price_rate or 0,
    "expense_account": frappe.db.get_value("Company", {"name":doc.company}, "default_expense_account"),
    "reference_purchase_receipt":frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "purchase_receipt"),
    "warehouse_location" : doc.scaned_location,
    "lot_number":doc.batch_no,
    "allow_zero_valuation_rate":1,
    "conversion_factor":1,
    "cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
    })
    se.flags.ignore_mandatory = True
    se.set_missing_values()
    se.docstatus=1
    se.insert(ignore_permissions=True)
    doc.stock_entry =se.name
    doc.save(ignore_permissions=True)
    update_quaity_status(doc)

def update_quaity_status(doc, handler=""):
    quality_lot= frappe.db.sql(
        """
        SELECT batch_no 
        FROM `tabQuality Inspection Page Table`
        WHERE batch_no = %(lot_no)s
        AND part_number =%(part_number)s """, values={"lot_no": doc.batch_no, "part_number":doc.part_number},as_dict=1,)
    print("///////",quality_lot)
    rejected_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "rejected_warehouse")
    accepted_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "quality_inspection_warehouse")
    hold_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "hold_warehouse")
    
    if quality_lot:
        if (doc.to_warehouse == accepted_warehouse) :
            frappe.db.sql("""UPDATE `tabQuality Inspection Page Table` set current_status="Accepted"
            where batch_no=%(lot_no)s and part_number=%(part_number)s""",{"lot_no":doc.batch_no,"part_number":doc.part_number})
        if (doc.to_warehouse == rejected_warehouse) :
            frappe.db.sql("""UPDATE `tabQuality Inspection Page Table` set current_status="Rejected"
            where batch_no=%(lot_no)s and part_number=%(part_number)s""",{"lot_no":doc.batch_no,"part_number":doc.part_number})
        if (doc.to_warehouse == hold_warehouse) :
            frappe.db.sql("""UPDATE `tabQuality Inspection Page Table` set current_status="On Hold"
            where batch_no=%(lot_no)s and part_number=%(part_number)s""",{"lot_no":doc.batch_no,"part_number":doc.part_number})
        