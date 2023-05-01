# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe
import json
from frappe import _
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
def search_lot(batch,company):
    # main_lot = frappe.db.get_value("Quality Inspection Page Table", {"batch_no": batch}, "lot_no")
    # print("////////////",main_lot)
    # if main_lot :
    #     stock = frappe.db.sql("""SELECT iw.name as grn,iwd.part_number,iwd.description,iwd.qty,iwd.batch_no,iwd.lot_no,iw.owner,(select location from `tabItem` where name=iwd.part_number) as location
	#     from `tabQuality Inspection Page` iw LEFT JOIN `tabQuality Inspection Page Table` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 and iwd.lot_no = '%(batch)s' """%{"batch": main_lot}, as_dict = 1)
    #     return stock
    # else :
    stock = frappe.db.sql("""SELECT iw.name as grn,iwd.part_number,iwd.description,iwd.qty,iwd.batch_no,iwd.lot_no,iw.owner,(select warehouse_location from `tabItem Default` where parent=iwd.part_number and company='%(company)s') as location
	from `tabQuality Inspection Page` iw LEFT JOIN `tabQuality Inspection Page Table` iwd ON (iw.name=iwd.parent) where iw.docstatus=1
    and  iwd.batch_no NOT IN (select `tabPutaway`.batch_no from `tabPutaway` where `tabPutaway`.docstatus=1 and `tabPutaway`.batch_no='%(batch)s') and iwd.batch_no = '%(batch)s' """%{"batch": batch,"company":company}, as_dict = 1)
    return stock
# def create_quality_inspection(doc, handler=""):
#     for item in doc.quality_inspection_page_table:
#         qi = frappe.new_doc("Quality Inspection")
#         qi.update({ "inspection_type": "Incoming" , "reference_type": "Purchase Receipt","reference_name": item.purchase_receipt,"status":item.status,"item_code":item.part_number,"lot_number":item.batch_no,"sample_size":item.qty,"inspected_by":doc.owner})
        
#         qi.docstatus=1
#         qi.insert()

def create_stock_entry(doc, handler=""):
    if doc.scaned_location == doc.location :
        se = frappe.new_doc("Stock Entry")
        se.update({ "purpose": "Material Transfer" , "stock_entry_type": "Material Transfer","putaway":doc.name})
        se.append("items", { 
        "item_code":doc.part_number,
        "qty": frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty"),
        "transfer_qty":frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty"),
        "s_warehouse": frappe.db.get_value("WMS Settings details", {"company":doc.company}, "quality_inspection_warehouse"),
        "t_warehouse": frappe.db.get_value("Warehouse Location", {"name":doc.location}, "warehouse"),
        "expense_account": frappe.db.get_value("Company", {"name":doc.company}, "default_expense_account"),
        "warehouse_location" : doc.location,
        "lot_number":doc.batch_no,
        "allow_zero_valuation_rate":1,
        "conversion_factor":1
        })
        se.flags.ignore_mandatory = True
        se.set_missing_values()
        se.docstatus=1
        se.insert(ignore_permissions=True)
    else :
        se = frappe.new_doc("Stock Entry")
        se.update({ "purpose": "Material Transfer" , "stock_entry_type": "Material Transfer","putaway":doc.name})
        se.append("items", { 
        "item_code":doc.part_number,
        "qty": frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty"),
        "transfer_qty":frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty"),
        "s_warehouse": frappe.db.get_value("WMS Settings details", {"company":doc.company}, "quality_inspection_warehouse"),
        "t_warehouse": frappe.db.get_value("Warehouse Location", {"name":doc.location}, "warehouse"),
        "expense_account": frappe.db.get_value("Company", {"name":doc.company}, "default_expense_account"),
        "warehouse_location" : frappe.db.get_value("WMS Settings details", {"company":doc.company}, "temporary_location"),
        "lot_number":doc.batch_no,
        "allow_zero_valuation_rate":1,
        "conversion_factor":1
        })
        se.flags.ignore_mandatory = True
        se.set_missing_values()
        se.docstatus=1
        se.insert(ignore_permissions=True)

@frappe.whitelist()
def update_part_number_location(item_code,company,update_location,location):
    item = frappe.get_doc('Item', item_code)
    if not location :
        item.append(
            "item_defaults",
            {
             "company": company,
             "warehouse_location": update_location,
             "default_warehouse": frappe.db.get_value("Warehouse Location", filters={"name": update_location}, fieldname="warehouse"),
             
             },
         )
        item.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint(
        _("Location successfully updated for Item: " + item.item_name), alert=True
        )
    if location :
        frappe.db.sql("""UPDATE `tabItem Default` set warehouse_location=%(update_location)s
        where parent=%(item_code)s and company=%(company)s""",{"update_location":update_location,"item_code":item_code,"company":company})
        # item.update(ignore_permissions=True)
        # frappe.db.commit()
        frappe.msgprint(
        _("Location successfully updated for Item: " + item.item_name), alert=True
        )