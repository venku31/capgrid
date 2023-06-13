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
    # hold_location = frappe.db.get_value("WMS Settings details", {"company":company,"main_warehouse":main_warehouse}, "default_hold_location")
    # rejection_location = frappe.db.get_value("WMS Settings details", {"company":company,"main_warehouse":main_warehouse}, "default_rejection_location")
    stock = frappe.db.sql("""SELECT iw.name as grn,iwd.part_number,iwd.description,iwd.accepted_qty,iwd.batch_no,iwd.lot_no,iw.owner,iwd.status,iw.main_warehouse,
    Case when iwd.status="Accepted" 
    then
    (select warehouse_location from `tabItem Default` where parent=iwd.part_number and company='%(company)s')
    when iwd.status="Rejected" 
    then (select default_rejection_location from `tabWMS Settings details` where company='%(company)s' and main_warehouse=iw.main_warehouse)
    when iwd.status="On Hold" then (select default_hold_location from `tabWMS Settings details` where company='%(company)s' and main_warehouse=iw.main_warehouse) 
    end as location
	from `tabQuality Inspection Page` iw LEFT JOIN `tabQuality Inspection Page Table` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 
    and  iwd.batch_no NOT IN (select `tabPutaway`.batch_no from `tabPutaway` where `tabPutaway`.docstatus=1 and `tabPutaway`.batch_no='%(batch)s') and iwd.batch_no = '%(batch)s' 
    UNION
    SELECT iw.name as grn,iwd.part_number,iwd.item_name as description,iwd.qty as accepted_qty,iwd.batch_no,iwd.lot_no,iw.owner,"Accepted" as status,iw.main_warehouse,
    (select warehouse_location from `tabItem Default` where parent=iwd.part_number and company='%(company)s') as location
    from `tabLot Number Generation` iw LEFT JOIN `tabLot Number Generation Item Details` iwd ON(iw.name=iwd.parent) where iw.docstatus=1 and iwd.batch_no = '%(batch)s' 
    """%{"batch": batch,"company":company}, as_dict = 1)
    return stock
# def create_quality_inspection(doc, handler=""):
#     for item in doc.quality_inspection_page_table:
#         qi = frappe.new_doc("Quality Inspection")
#         qi.update({ "inspection_type": "Incoming" , "reference_type": "Purchase Receipt","reference_name": item.purchase_receipt,"status":item.status,"item_code":item.part_number,"lot_number":item.batch_no,"sample_size":item.qty,"inspected_by":doc.owner})
        
#         qi.docstatus=1
#         qi.insert()

def create_stock_entry(doc, handler=""):
    # if doc.scaned_location == doc.location :
    se = frappe.new_doc("Stock Entry")
    se.update({ "purpose": "Repack" , "stock_entry_type": "Repack","company":doc.company,"putaway":doc.name})
    item_code = doc.part_number
    po = frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "purchase_order") 
    po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':doc.part_number,'parent':po}, 'rate')
    last_rate = frappe.db.get_value('Item', {'item_code':doc.part_number}, 'last_purchase_rate')
    item_price_rate = frappe.db.get_value('Item Price', {'item_code':doc.part_number,'price_list':"Standard Buying"}, 'price_list_rate')
    if doc.lot_status=="Accepted" :
        location = ""
    else :
        location = doc.location
    se.append("items", { 
    "item_code":doc.part_number,
    "qty": frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "rejected_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "hold_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "lot_qty"),
    "transfer_qty":frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "rejected_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "hold_qty"),
    "s_warehouse": frappe.db.get_value("Warehouse Location", {"company":doc.company,"main_warehouse":doc.main_warehouse,"location":doc.location}, "warehouse"),
    "t_warehouse": "",
    "set_basic_rate_manually":1,
    # "basic_rate" : frappe.db.get_value('Item', {'item_code':doc.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':doc.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
    "basic_rate" :doc.last_purchase_rate,
    "valuation_rate" :doc.last_purchase_rate,
    "expense_account": frappe.db.get_value("Company", {"name":doc.company}, "stock_adjustment_account"),
    "reference_purchase_receipt":frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "purchase_receipt"),
    "warehouse_location" : location,
    "lot_number":doc.batch_no,
    "allow_zero_valuation_rate":1,
    "conversion_factor":1,
    "cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
    })
    se.append("items", { 
    "item_code":doc.part_number,
    "qty": frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "rejected_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "hold_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "lot_qty"),
    "transfer_qty":frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "rejected_qty") or frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "hold_qty"),
    "s_warehouse": "",
    "t_warehouse": frappe.db.get_value("Warehouse Location", {"company":doc.company,"main_warehouse":doc.main_warehouse,"name":doc.scaned_location}, "warehouse"),
    "is_finished_item":1,
    "set_basic_rate_manually":1,
    # "basic_rate" : frappe.db.get_value('Item', {'item_code':doc.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':doc.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
    "basic_rate" :doc.last_purchase_rate,
    "valuation_rate" :doc.last_purchase_rate,
    "expense_account": frappe.db.get_value("Company", {"name":doc.company}, "stock_adjustment_account"),
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
    # else :
    #     se = frappe.new_doc("Stock Entry")
    #     se.update({ "purpose": "Material Transfer" , "stock_entry_type": "Material Transfer","putaway":doc.name})
    #     se.append("items", { 
    #     "item_code":doc.part_number,
    #     "qty": frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty"),
    #     "transfer_qty":frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "accepted_qty"),
    #     "s_warehouse": frappe.db.get_value("WMS Settings details", {"company":doc.company}, "quality_inspection_warehouse"),
    #     "t_warehouse": frappe.db.get_value("Warehouse Location", {"name":doc.location}, "warehouse"),
    #     "expense_account": frappe.db.get_value("Company", {"name":doc.company}, "default_expense_account"),
    #     "warehouse_location" : frappe.db.get_value("WMS Settings details", {"company":doc.company}, "temporary_location"),
    #     "reference_purchase_receipt":frappe.db.get_value("Lot Number", {"name":doc.batch_no}, "purchase_receipt"),
    #     "lot_number":doc.batch_no,
    #     "allow_zero_valuation_rate":1,
    #     "conversion_factor":1
    #     })
    #     se.flags.ignore_mandatory = True
    #     se.set_missing_values()
    #     se.docstatus=1
    #     se.insert(ignore_permissions=True)
    #     doc.stock_entry =se.name

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

@frappe.whitelist()        
def update_item_location(doc, handler=""):
    if not doc.location:
        # item_default = frappe.get_doc('Item Default',{"parent":doc.part_number,"company":doc.company})
        item_default= frappe.db.sql(
        """
        SELECT name 
        FROM `tabItem Default`
        WHERE company = %(company)s
        AND parent =%(part_number)s """, values={"company": doc.company, "part_number":doc.part_number},as_dict=1,)
        print("///////",item_default)
        company=doc.company
        scaned_location=doc.scaned_location
        itemcode=doc.part_number
        if item_default:
            frappe.db.sql("""UPDATE `tabItem Default` set warehouse_location=%(scaned_location)s
            where parent=%(itemcode)s and company=%(company)s""",{"scaned_location":scaned_location,"itemcode":doc.part_number,"company":company})
            doc.location=doc.scaned_location
        else :
            item = frappe.get_doc('Item', doc.part_number)
            item.append(
            "item_defaults",
            {
             "company": doc.company,
             "warehouse_location": doc.scaned_location,
             "default_warehouse": frappe.db.get_value("Warehouse Location", filters={"name": doc.scaned_location}, fieldname="warehouse"),
            },
            )
            item.flags.ignore_mandatory = True
            item.save(ignore_permissions=True)
            doc.location=doc.scaned_location
