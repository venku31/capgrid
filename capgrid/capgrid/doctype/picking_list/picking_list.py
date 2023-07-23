# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PickingList(Document):
	# pass
    def on_update(doc):
         exists = frappe.db.get_value("PickList",{"name":doc.picklist},"name")
         if exists :
            workflow_state=frappe.db.get_value("PickList",{"name":doc.picklist},"workflow_state")
            if workflow_state == "Pending" and doc.total_scaned_qty  :
                frappe.db.sql("""
				update `tabPickList` 
					set workflow_state = "Picking Started"
					where docstatus<2 AND name = "{picklist}";""".format(picklist = doc.picklist))
            

            if doc.part_details :
                for row in doc.part_details:
                    qty = frappe.db.sql(""" Select sum(`tabPicking List Item Details`.qty) as qty from `tabPicking List` LEFT JOIN `tabPicking List Item Details` ON (`tabPicking List`.name=`tabPicking List Item Details`.parent) where `tabPicking List`.picklist ="{picklist}"
                    and `tabPicking List Item Details`.part_number="{part_number}" group by `tabPicking List Item Details`.part_number;""".format(picklist = doc.picklist,part_number=row.part_number))
                    frappe.db.sql("""
				    update `tabPickList Details` 
					set total_picked_qty = {qty}
					where parent = "{picklist}" AND part_number="{part_number}";""".format(picklist = doc.picklist,part_number=row.part_number,qty=qty[0][0]))
                    frappe.db.commit()



@frappe.whitelist()
def get_stock_warehouse_locations(company, warehouse,item_code):
	# stock = frappe.db.sql(""" SELECT sle.item_code,
    #         sle.warehouse,
    #         sle.warehouse_location,
    #         sle.lot_number,
    #         sle.posting_date,
    #         sle.actual_qty
    #     FROM `tabStock Ledger Entry` sle
    #     where (sle.docstatus < 2) and (sle.is_cancelled = 0) and sle.warehouse_location !="" and 
	# 	sle.actual_qty>0 and sle.warehouse='%(warehouse)s' and sle.company='%(company)s'  
    #     order by posting_date desc, posting_time desc, creation desc limit 1 
    #     """ %{"warehouse": warehouse,"company":company}, as_dict = 1)
	stock = frappe.db.sql(""" SELECT            
        sle.warehouse_location,sum(sle.actual_qty) as actual_qty
        FROM `tabStock Ledger Entry` sle
        where (sle.docstatus < 2) and (sle.is_cancelled = 0) and sle.item_code ='%(item_code)s' and sle.warehouse='%(warehouse)s'
	    and sle.company='%(company)s' and sle.warehouse_location !=""
        group by sle.warehouse_location
        order by posting_date desc
        """ %{"warehouse": warehouse,"item_code":item_code,"company":company}, as_dict = 1)
	return stock

@frappe.whitelist()
def scan_lot(lot_no,warehouse_location,company):
    stock = frappe.db.sql("""SELECT            
        sle.lot_number,sle.item_code,sle.stock_uom,sle.warehouse_location,sle.actual_qty as actual_qty
        FROM `tabStock Ledger Entry` sle
        where (sle.docstatus < 2) and (sle.is_cancelled = 0) and sle.lot_number ='%(lot_no)s' and sle.warehouse_location='%(warehouse_location)s' and sle.company='%(company)s' and sle.warehouse_location !="" 
        order by posting_date desc 
    """%{"lot_no": lot_no,"company":company,"warehouse_location":warehouse_location}, as_dict = 1)
    return stock

@frappe.whitelist()
def picklist_item_query(doctype, txt, searchfield, start, page_len, filters):
    if filters.get("parent"):
        return frappe.db.sql(""" select part_number,part_number_name,to_be_picked from `tabPickList Details`
        where parent = %(parent)s and part_number_name like %(txt)s
        limit %(start)s, %(page_len)s""", {
            'parent': filters.get("parent"),
            'start': start,
            'page_len': page_len,
            'txt': "%%%s%%" % txt
        })
    else :
        return frappe.db.sql(""" select name,item_name,stock_uom from `tabItem`
        where item_name like %(txt)s
        limit %(start)s, %(page_len)s""", {
            'start': start,
            'page_len': page_len,
            'txt': "%%%s%%" % txt
        })
    
@frappe.whitelist()
def picklist_item_qty(part_number,picklist):
    stock = frappe.db.sql("""Select to_be_picked from `tabPickList Details` where docstatus<2 and parent ='%(picklist)s' and part_number='%(part_number)s' 
    """%{"picklist": picklist,"part_number":part_number}, as_dict = 1)
    return stock



     