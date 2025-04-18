# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt


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

class QualityInspectionPage(Document):
    def validate(self):
        for row in self.quality_inspection_page_table:
            exists = frappe.get_value("Quality Inspection Page Table", {"batch_no": row.batch_no, "docstatus": 1}, 'parent')
            if exists:
                frappe.throw(_("QI already done for this Lot {0} in Quality Inspection :<b>{1}</b>").format(row.batch_no, exists))

        existing_grn = frappe.get_value("YourGRNDoctype", {"grn_field": self.grn, "docstatus": 1}, 'name')
        if existing_grn:
            frappe.throw(_("GRN '{0}' already exists in Quality Inspection Page '{1}'").format(self.grn, existing_grn))
    

@frappe.whitelist()
def search_lot(batch,):
    # item_data = search_serial_or_batch_or_barcode_number(batch)
    # if item_data != 0:
    # main_lot = frappe.db.sql("""SELECT parent_lot from `tabLot Number` where name='%(batch)s' """%{"batch": batch}, as_dict = 1)
    qi_lot = frappe.db.get_value("Quality Inspection Page Table", {"batch_no": batch,"docstatus":1}, "lot_no")
    main_lot = frappe.db.get_value("GRN Inward Item Details", {"batch_no": batch}, "lot_no")
    #print("////////////",qi_lot)
    if not qi_lot :
        if main_lot :
            stock = frappe.db.sql("""SELECT iw.name as grn,iw.purchase_order,iw.purchase_receipt,iwd.part_number,iwd.item_name,iwd.packet,iwd.qty,iwd.batch_no,iwd.lot_no,iw.supplier,iw.supplier_name,iw.supplier_invoice_no,iw.supplier_invoice_date,iw.owner,iw.main_warehouse,iw.company
            from `tabGRN Inward` iw LEFT JOIN `tabGRN Inward Item Details` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 and iwd.lot_no = '%(batch)s' order by iwd.batch_no  """%{"batch": main_lot}, as_dict = 1)
            return stock
        else :
            stock = frappe.db.sql("""SELECT iw.name as grn,iw.purchase_order,iw.purchase_receipt,iwd.part_number,iwd.item_name,iwd.packet,iwd.qty,iwd.batch_no,iwd.lot_no,iw.supplier,iw.supplier_name,iw.supplier_invoice_no,iw.supplier_invoice_date,iw.owner,iw.main_warehouse,iw.company
            from `tabGRN Inward` iw LEFT JOIN `tabGRN Inward Item Details` iwd ON (iw.name=iwd.parent) where iw.docstatus=1 and iwd.lot_no = '%(batch)s' order by iwd.batch_no  """%{"batch": batch}, as_dict = 1)
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
    # update_purchase_receipt(doc)
    # create_qi_stock_entry(doc)

def update_lot(doc):
    for row in doc.quality_inspection_page_table:
        if row.batch_no :
            lot = frappe.get_doc('Lot Number', row.batch_no)
   
            lot.quality_inspection_page = doc.name
            lot.lot_qty = row.qty
            lot.accepted_qty = row.accepted_qty
            lot.rejected_qty = row.rejected_qty
            lot.hold_qty = row.hold_qty
            lot.purchase_receipt = doc.purchase_receipt
            lot.created_by = doc.created_by
            lot.save(ignore_permissions=True)
            frappe.db.commit()
def update_main_lot(doc):
    lot_no=frappe.db.get_value("GRN Inward Item",{"parent":doc.grn},'lot_no')
    if lot_no :
        lot = frappe.get_doc('Lot Number',lot_no)
        lot.quality_inspection_page = doc.name
        lot.lot_qty = doc.total_inward_qty
        lot.accepted_qty = doc.total_accepted_qty
        lot.rejected_qty = doc.total_rejected_qty
        lot.purchase_receipt = doc.purchase_receipt
        lot.created_by = doc.created_by
        lot.save(ignore_permissions=True)
        frappe.db.commit()

def update_purchase_receipt(doc):
    pr = frappe.get_doc('Purchase Receipt',doc.purchase_receipt)
    if pr :
        for item in pr.items:
            # pr.set_warehouse="Finish Goods-Faridabad - CAPGRID-GURGAON"
            pr.rejected_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company}, "rejected_warehouse")
            pr.set_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company}, "quality_inspection_warehouse")
            item.received_qty = doc.total_accepted_qty+doc.total_rejected_qty
            item.qty = doc.total_accepted_qty
            item.rejected_qty = doc.total_rejected_qty
            item.rejected_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company}, "rejected_warehouse")
            item.warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company}, "quality_inspection_warehouse")
            item.warehouse_location = ""
            pr.flags.ignore_mandatory = True
            pr.docstatus=1
            pr.save(ignore_permissions=True)
            frappe.db.commit()

def validate_lot_no(self,method=None):
    # if self.grn:
    # for row in self.quality_inspection_page_table:
    lot = frappe.db.sql('''select parent,batch_no from `tabQuality Inspection Page Table`
         where
                batch_no = %(lot_no)s
                and name != %(name)s
                and docstatus < 2  ''',{
                    "lot_no": self.scan_barcode,
                    "name": self.name
                } )
 
    if lot:
        lot = lot[0][0]
        frappe.throw(_("Quality Inspection exists in  {0}".format(lot)))



def create_qi_stock_entry(doc, handler=""):
    s_warehouse = frappe.db.get_value("WMS Settings details", {"company": doc.company, "main_warehouse": doc.main_warehouse}, "inward_warehouse")
    accepted_warehouse = frappe.db.get_value("WMS Settings details", {"company": doc.company, "main_warehouse": doc.main_warehouse}, "quality_inspection_warehouse")
    rejected_warehouse = frappe.db.get_value("WMS Settings details", {"company": doc.company, "main_warehouse": doc.main_warehouse}, "rejected_warehouse")
    hold_warehouse = frappe.db.get_value("WMS Settings details", {"company": doc.company, "main_warehouse": doc.main_warehouse}, "hold_warehouse")
    hold_location = frappe.db.get_value("WMS Settings details", {"company": doc.company, "main_warehouse": doc.main_warehouse}, "default_hold_location")
    rejection_location = frappe.db.get_value("WMS Settings details", {"company": doc.company, "main_warehouse": doc.main_warehouse}, "default_rejection_location")
    expense_account = frappe.db.get_value("Company", {"name": doc.company}, "stock_adjustment_account")
    cost_center = frappe.db.get_value("Company", {"name": doc.company}, "cost_center")

    se = frappe.new_doc("Stock Entry")
    se.update({"purpose": "Repack", "stock_entry_type": "Repack", "company": doc.company})

    for se_item in doc.quality_inspection_page_table:
        # Fetching valuation rate directly from GRN Inward Item Details table
        valuation_rate_query = """
        SELECT details.batch_no, item.part_number, item.lot_no, item.rate, item.qty
        FROM `tabGRN Inward Item` AS item
        INNER JOIN `tabGRN Inward Item Details` AS details ON item.parent = details.parent
        WHERE details.part_number = "{0}" AND (details.lot_no = "{1}" OR details.batch_no = "{1}")
        """.format(se_item.part_number, se_item.batch_no)

        valuation_rate_details = frappe.db.sql(valuation_rate_query, as_dict=True)
        if valuation_rate_details:
            valuation_rate = valuation_rate_details[0].get('rate', 0.00)
        else:
            valuation_rate = 0.00

        if se_item.accepted_qty:
            # Common logic for accepted_qty
            print(f"Accepted: Item Code: {se_item.part_number}, Warehouse: {s_warehouse}, Lot Number: {se_item.batch_no}, Valuation Rate: {valuation_rate}")

            se.append("items",
                      {"item_code": se_item.part_number,
                       "qty": se_item.accepted_qty,
                       "s_warehouse": s_warehouse,
                       "t_warehouse": "",
                       "transfer_qty": se_item.accepted_qty,
                       "set_basic_rate_manually": 0,
                       "basic_rate": valuation_rate,
                       "valuation_rate": valuation_rate,
                       "basic_amount": se_item.accepted_qty * valuation_rate,
                       "amount": se_item.accepted_qty * valuation_rate,
                       "conversion_factor": 1,
                       "allow_zero_valuation_rate": 0,
                       "reference_purchase_receipt": doc.purchase_receipt,
                       "lot_number": se_item.batch_no,
                       "expense_account": expense_account,
                       "cost_center": cost_center
                       })
            se.append("items",
                      {"item_code": se_item.part_number,
                       "qty": se_item.accepted_qty,
                       "s_warehouse": "",
                       "t_warehouse": accepted_warehouse,
                       "transfer_qty": se_item.accepted_qty,
                       "set_basic_rate_manually": 0,
                       "basic_rate": valuation_rate,
                       "valuation_rate": valuation_rate,
                       "basic_amount": se_item.accepted_qty * valuation_rate,
                       "amount": se_item.accepted_qty * valuation_rate,
                       "conversion_factor": 1,
                       "is_finished_item": 1,
                       "allow_zero_valuation_rate": 0,
                       "reference_purchase_receipt": doc.purchase_receipt,
                       "lot_number": se_item.batch_no,
                       "expense_account": expense_account,
                       "cost_center": cost_center
                       })

        if se_item.rejected_qty or se_item.hold_qty:
            # Common logic for both rejected_qty and hold_qty
            qty_to_process = se_item.rejected_qty if se_item.rejected_qty else se_item.hold_qty
            warehouse_to_use = rejected_warehouse if se_item.rejected_qty else hold_warehouse
            location_to_use = rejection_location if se_item.rejected_qty else hold_location

            po_rate = frappe.db.get_value('Purchase Order Item', {'item_code': se_item.part_number, 'parent': doc.purchase_order}, 'rate')
            last_rate = frappe.db.get_value('Item', {'item_code': se_item.part_number}, 'last_purchase_rate')
            item_price_rate = frappe.db.get_value('Item Price', {'item_code': se_item.part_number, 'price_list': "Standard Buying"}, 'price_list_rate')
            item_bin_rate = frappe.db.get_value('Bin', {'item_code': se_item.part_number, 'warehouse': s_warehouse}, 'valuation_rate')
            item_val_rate = frappe.db.get_value('Item', {'item_code': se_item.part_number}, 'valuation_rate')
            base_rate = item_bin_rate or item_val_rate or last_rate or 0.00

            se.append("items", {"item_code": se_item.part_number, "qty": qty_to_process, "s_warehouse": s_warehouse,
                                "t_warehouse": "",
                                "transfer_qty": qty_to_process, "conversion_factor": 1, "allow_zero_valuation_rate": 0,
                                "reference_purchase_receipt": doc.purchase_receipt,
                                "set_basic_rate_manually": 0,
                                "basic_rate": base_rate,  # se_item.last_purchase_rate,
                                "valuation_rate": base_rate,  # se_item.last_purchase_rate,
                                "basic_amount": qty_to_process * base_rate,  # se_item.last_purchase_rate,
                                "amount": qty_to_process * base_rate,  # se_item.last_purchase_rate,
                                "lot_number": se_item.batch_no, "expense_account": expense_account,
                                "cost_center": frappe.db.get_value("Company", {"name": doc.company}, "cost_center")})
            se.append("items", {"item_code": se_item.part_number, "qty": qty_to_process,
                                "s_warehouse": "",
                                "t_warehouse": warehouse_to_use,
                                "transfer_qty": qty_to_process,
                                "set_basic_rate_manually": 0,
                                "basic_rate": base_rate,  # se_item.last_purchase_rate,
                                "valuation_rate": base_rate,  # se_item.last_purchase_rate,
                                "basic_amount": qty_to_process * base_rate,  # se_item.last_purchase_rate,
                                "amount": qty_to_process * base_rate,  # se_item.last_purchase_rate,
                                "conversion_factor": 1, "is_finished_item": 1, "allow_zero_valuation_rate": 0,
                                "reference_purchase_receipt": doc.purchase_receipt, "lot_number": se_item.batch_no,
                                "warehouse_location": location_to_use,
                                "expense_account": expense_account,
                                "cost_center": frappe.db.get_value("Company", {"name": doc.company}, "cost_center")})

    # Saving the stock entry directly
    se.flags.ignore_mandatory = True
    se.set_missing_values()
    se.docstatus = 1
    se.insert(ignore_permissions=True)
    doc.stock_entry = se.name
    doc.save(ignore_permissions=True)


# def create_qi_stock_entry(doc, handler=""):
#     # for se_item in doc.quality_inspection_page_table:
#         s_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "inward_warehouse")
#         accepted_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "quality_inspection_warehouse")
#         rejected_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "rejected_warehouse")
#         hold_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "hold_warehouse")
#         hold_location = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "default_hold_location")
#         rejection_location = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "default_rejection_location")
#         expense_account = frappe.db.get_value("Company", {"name":doc.company}, "stock_adjustment_account")
#         cost_center = frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
#         # try:
#         se = frappe.new_doc("Stock Entry")
#         # se.update({ "purpose": "Material Transfer" , "stock_entry_type": "Material Transfer","company":doc.company})
#         se.update({ "purpose": "Repack" , "stock_entry_type": "Repack","company":doc.company})
#             # if se_item.accepted_qty:
#             # items=[]
#         for se_item in doc.quality_inspection_page_table:
#             po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':se_item.part_number,'parent':doc.purchase_order}, 'rate')
#             last_rate = frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate')
#             item_price_rate = frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate')
#             item_bin_rate = frappe.db.get_value('Bin', {'item_code':se_item.part_number,'warehouse':s_warehouse}, 'valuation_rate')
#             item_val_rate = frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'valuation_rate')
#             base_rate = item_bin_rate or item_val_rate or last_rate or 0.00
#             if se_item.accepted_qty:
#                 se.append("items", 
#                 { "item_code":se_item.part_number,
#                 "qty": se_item.accepted_qty,
#                 "s_warehouse": s_warehouse,
#                 "t_warehouse": "",
#                 "transfer_qty" : se_item.accepted_qty,
#                 "set_basic_rate_manually":0,
#                 # "basic_rate" : frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
#                 "basic_rate" : base_rate, # se_item.last_purchase_rate,
#                 "valuation_rate" : base_rate,#se_item.last_purchase_rate,
#                 "basic_amount" : se_item.accepted_qty*base_rate,#se_item.last_purchase_rate,
#                 "amount" : se_item.accepted_qty*base_rate,#se_item.last_purchase_rate,
#                 # "basic_rate" : se_item.last_purchase_rate,
#                 # "valuation_rate" : se_item.last_purchase_rate,
#                 # "basic_amount" : se_item.accepted_qty*se_item.last_purchase_rate,
#                 # "amount" : se_item.accepted_qty*se_item.last_purchase_rate,
#                 "conversion_factor": 1,
#                 "allow_zero_valuation_rate":0,
#                 "reference_purchase_receipt":doc.purchase_receipt,
#                 "lot_number":se_item.batch_no,
#                 "expense_account":expense_account,
#                 "cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
#                 })
#                 se.append("items", 
#                 { "item_code":se_item.part_number,
#                 "qty": se_item.accepted_qty,
#                 "s_warehouse": "",
#                 "t_warehouse": accepted_warehouse,
#                 "transfer_qty" : se_item.accepted_qty,
#                 "set_basic_rate_manually":0,
#                 # "basic_rate" : frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
#                 "basic_rate" : base_rate, #se_item.last_purchase_rate,
#                 "valuation_rate" : base_rate,#se_item.last_purchase_rate,
#                 "basic_amount" : se_item.accepted_qty*base_rate,#se_item.last_purchase_rate,
#                 "amount" : se_item.accepted_qty*base_rate,#se_item.last_purchase_rate,
#                 # "basic_rate" : se_item.last_purchase_rate,
#                 # "valuation_rate" : se_item.last_purchase_rate,
#                 # "basic_amount" : se_item.accepted_qty*se_item.last_purchase_rate,
#                 # "amount" : se_item.accepted_qty*se_item.last_purchase_rate,
#                 "conversion_factor": 1,
#                 "is_finished_item":1,
#                 "allow_zero_valuation_rate":0,
#                 "reference_purchase_receipt":doc.purchase_receipt,
#                 "lot_number":se_item.batch_no,
#                 "expense_account":expense_account,
#                 "cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
#                 })
#             if se_item.rejected_qty:
#                 se.append("items", { "item_code":se_item.part_number, "qty": se_item.rejected_qty,"s_warehouse": s_warehouse,
#                 "t_warehouse": "",
#                 "transfer_qty" : se_item.rejected_qty,"conversion_factor": 1,"allow_zero_valuation_rate":0,"reference_purchase_receipt":doc.purchase_receipt,
#                 "set_basic_rate_manually":0,
#                 # "basic_rate" : frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
#                 "basic_rate" : base_rate, #se_item.last_purchase_rate,
#                 "valuation_rate" : base_rate,#se_item.last_purchase_rate,
#                 "basic_amount" : se_item.rejected_qty*base_rate,#se_item.last_purchase_rate,
#                 "amount" : se_item.rejected_qty*base_rate,#se_item.last_purchase_rate,
#                 # "basic_rate" : se_item.last_purchase_rate,
#                 # "valuation_rate" : se_item.last_purchase_rate,
#                 # "basic_amount" : se_item.rejected_qty*se_item.last_purchase_rate,
#                 # "amount" : se_item.rejected_qty*se_item.last_purchase_rate,
#                 "lot_number":se_item.batch_no,"expense_account":expense_account,
#                 "cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")})
#                 se.append("items", { "item_code":se_item.part_number, "qty": se_item.rejected_qty,
#                 "s_warehouse": "",
#                 "t_warehouse": rejected_warehouse,
#                 "transfer_qty" : se_item.rejected_qty,
#                 "set_basic_rate_manually":0,
#                 # "basic_rate" : frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
#                 "basic_rate" : base_rate, #se_item.last_purchase_rate,
#                 "valuation_rate" : base_rate,#se_item.last_purchase_rate,
#                 "basic_amount" : se_item.rejected_qty*base_rate,#se_item.last_purchase_rate,
#                 "amount" : se_item.rejected_qty*base_rate,#se_item.last_purchase_rate,
#                 # "basic_rate" : se_item.last_purchase_rate,
#                 # "valuation_rate" : se_item.last_purchase_rate,
#                 # "basic_amount" : se_item.rejected_qty*se_item.last_purchase_rate,
#                 # "amount" : se_item.rejected_qty*se_item.last_purchase_rate,
#                 "conversion_factor": 1,"is_finished_item":1,"allow_zero_valuation_rate":0,"reference_purchase_receipt":doc.purchase_receipt,
#                 "lot_number":se_item.batch_no,"warehouse_location":rejection_location,"expense_account":expense_account,
#                 "cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")})
#             if se_item.hold_qty :
#                 se.append("items", { "item_code":se_item.part_number, "qty": se_item.hold_qty,"s_warehouse": s_warehouse,
#                 "t_warehouse": "",
#                 "transfer_qty" : se_item.hold_qty,
#                 "set_basic_rate_manually":0,
#                 # "basic_rate" : frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
#                 "basic_rate" : base_rate, #se_item.last_purchase_rate,
#                 "valuation_rate" : base_rate,#se_item.last_purchase_rate,
#                 "basic_amount" : se_item.hold_qty*base_rate,#se_item.last_purchase_rate,
#                 "amount" : se_item.hold_qty*base_rate,#se_item.last_purchase_rate,
#                 # "basic_rate" : se_item.last_purchase_rate,
#                 # "valuation_rate" : se_item.last_purchase_rate,
#                 # "basic_amount" : se_item.hold_qty*se_item.last_purchase_rate,
#                 # "amount" : se_item.hold_qty*se_item.last_purchase_rate,
#                 "conversion_factor": 1,"allow_zero_valuation_rate":0,
#                 "reference_purchase_receipt":doc.purchase_receipt,"lot_number":se_item.batch_no,
#                 "expense_account":expense_account,"cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")})
#                 se.append("items", { "item_code":se_item.part_number, "qty": se_item.hold_qty,
#                 "s_warehouse": "",
#                 "t_warehouse": hold_warehouse,"transfer_qty" : se_item.hold_qty,
#                 "set_basic_rate_manually":0,
#                 # "basic_rate" : frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
#                 "basic_rate" : base_rate, #se_item.last_purchase_rate,
#                 "valuation_rate" : base_rate,#se_item.last_purchase_rate,
#                 "basic_amount" : se_item.hold_qty*base_rate,#se_item.last_purchase_rate,
#                 "amount" : se_item.hold_qty*base_rate,#se_item.last_purchase_rate,
#                 # "basic_rate" : se_item.last_purchase_rate,
#                 # "valuation_rate" : se_item.last_purchase_rate,
#                 # "basic_amount" : se_item.hold_qty*se_item.last_purchase_rate,
#                 # "amount" : se_item.hold_qty*se_item.last_purchase_rate,
#                 "conversion_factor": 1,"is_finished_item":1,"allow_zero_valuation_rate":0,
#                 "reference_purchase_receipt":doc.purchase_receipt,"lot_number":se_item.batch_no,"warehouse_location":hold_location,
#                 "expense_account":expense_account,"cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")})
            
#         se.flags.ignore_mandatory = True
#         se.set_missing_values()
#         se.docstatus=1
#         se.insert(ignore_permissions=True)
#         doc.stock_entry =se.name
#         doc.save(ignore_permissions=True)
#         # except Exception as e:
#         #     return {"error":e} 
        
@frappe.whitelist()
def create_status_stock_entry(company,main_warehouse,purchase_order,purchase_receipt,product_description):
    # for se_item in doc.quality_inspection_page_table:
        s_warehouse = frappe.db.get_value("WMS Settings details", {"company":company,"main_warehouse":main_warehouse}, "inward_warehouse")
        accepted_warehouse = frappe.db.get_value("WMS Settings details", {"company":company,"main_warehouse":main_warehouse}, "quality_inspection_warehouse")
        rejected_warehouse = frappe.db.get_value("WMS Settings details", {"company":company,"main_warehouse":main_warehouse}, "rejected_warehouse")
        hold_warehouse = frappe.db.get_value("WMS Settings details", {"company":company,"main_warehouse":main_warehouse}, "hold_warehouse")
        hold_location = frappe.db.get_value("WMS Settings details", {"company":company,"main_warehouse":main_warehouse}, "default_hold_location")
        rejection_location = frappe.db.get_value("WMS Settings details", {"company":company,"main_warehouse":main_warehouse}, "default_rejection_location")
        expense_account = frappe.db.get_value("Company", {"name":company}, "stock_adjustment_account")
        cost_center = frappe.db.get_value("Company", {"name":company}, "cost_center")
        # try:
        se = frappe.new_doc("Stock Entry")
        # se.update({ "purpose": "Material Transfer" , "stock_entry_type": "Material Transfer","company":doc.company})
        product = json.loads(product_description)
        se.update({ "purpose": "Repack" , "stock_entry_type": "Repack","company":company})
            # if se_item.accepted_qty:
            # items=[]
        for se_item in product:
            po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':se_item["part_number"],'parent':purchase_order}, 'rate')
            item_price_rate = frappe.db.get_value('Item Price', {'item_code':se_item["part_number"],'price_list':"Standard Buying"}, 'price_list_rate')
            if se_item["current_status"]:
                if se_item["accepted_qty"] and se_item["current_status"]=="Rejected":
                    se.append("items", 
                    { "item_code":se_item["part_number"],
                    "qty": se_item["accepted_qty"],
                    "s_warehouse": s_warehouse,
                    "t_warehouse": "",
                    "transfer_qty" : se_item["accepted_qty"],
                    "set_basic_rate_manually":0,
                    "basic_rate" : po_rate, # or item_price_rate or 0,
                    "conversion_factor": 1,
                    "allow_zero_valuation_rate":0,
                    "reference_purchase_receipt":purchase_receipt,
                    "lot_number":se_item["batch_no"],
                    "expense_account":expense_account,
                    "cost_center" : frappe.db.get_value("Company", {"name":company}, "cost_center")
                    })
                    se.append("items", 
                    { "item_code":se_item["part_number"],
                    "qty": se_item["accepted_qty"],
                
                    "s_warehouse": "",
                    "t_warehouse": rejected_warehouse,
                    "transfer_qty" : se_item["accepted_qty"],
                    "set_basic_rate_manually":0,
                    "basic_rate" : po_rate,# or item_price_rate or 0,
                    "conversion_factor": 1,
                    "is_finished_item":1,
                    "allow_zero_valuation_rate":0,
                    "reference_purchase_receipt":purchase_receipt,
                    "lot_number":se_item["batch_no"],
                    "expense_account":expense_account,
                    "cost_center" : frappe.db.get_value("Company", {"name":company}, "cost_center")
                    })
            
            
        se.flags.ignore_mandatory = True
        se.set_missing_values()
        se.docstatus=1
        se.insert(ignore_permissions=True)
        # stock_entry =se.name
        # doc.save(ignore_permissions=True)
def create_qi_status_change_entry(doc, handler=""):
    # for se_item in doc.quality_inspection_page_table:
        s_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "inward_warehouse")
        accepted_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "quality_inspection_warehouse")
        rejected_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "rejected_warehouse")
        hold_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "hold_warehouse")
        hold_location = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "default_hold_location")
        rejection_location = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "default_rejection_location")
        expense_account = frappe.db.get_value("Company", {"name":doc.company}, "stock_adjustment_account")
        cost_center = frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
        # try:
        if doc.docstatus==1 :
            se = frappe.new_doc("Stock Entry")
            # se.update({ "purpose": "Material Transfer" , "stock_entry_type": "Material Transfer","company":doc.company})
            se.update({ "purpose": "Repack" , "stock_entry_type": "Repack","company":doc.company})
                # if se_item.accepted_qty:
                # items=[]
            for se_item in doc.quality_inspection_page_table:
                po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':se_item.part_number,'parent':doc.purchase_order}, 'rate')
                item_price_rate = frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate')
                if se_item.current_status:
                    if (se_item.current_status=="Accepted" and se_item.status == "Rejected"):
                        se.append("items", 
                        {"item_code":se_item.part_number,
                        "qty": se_item.qty,
                        "s_warehouse": rejected_warehouse,
                        "t_warehouse": "",
                        "transfer_qty" : se_item.qty,
                        "set_basic_rate_manually":0,
                        "basic_rate" : po_rate,# or item_price_rate or 0,
                        "conversion_factor": 1,
                        "allow_zero_valuation_rate":0,
                        "reference_purchase_receipt":doc.purchase_receipt,
                        "lot_number":se_item.batch_no,
                        "expense_account":expense_account,"warehouse_location":rejection_location,
                        "cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
                        })
                        se.append("items", 
                        { "item_code":se_item.part_number,
                        "qty": se_item.qty,
                
                        "s_warehouse": "",
                        "t_warehouse": accepted_warehouse,
                        "transfer_qty" : se_item.qty,
                        "set_basic_rate_manually":0,
                        "basic_rate" : po_rate,# or item_price_rate or 0,
                        "conversion_factor": 1,
                        "is_finished_item":1,
                        "allow_zero_valuation_rate":0,
                        "reference_purchase_receipt":doc.purchase_receipt,
                        "lot_number":se_item.batch_no,
                        "expense_account":expense_account,
                        "cost_center" : frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
                        })
    
            
            se.flags.ignore_mandatory = True
            se.set_missing_values()
            # se.docstatus=1
            se.insert(ignore_permissions=True)
            # doc.stock_entry =se.name
            doc.save(ignore_permissions=True)