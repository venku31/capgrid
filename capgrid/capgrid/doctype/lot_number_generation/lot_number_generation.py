# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, add_months, today, add_days, nowdate,formatdate
import json
from toolz import excepts, first, compose
from frappe.model.db_query import DatabaseQuery
from frappe.desk.reportview import get_match_cond, get_filters_cond
from erpnext.accounts.utils import get_account_currency, get_fiscal_year
from erpnext.stock.doctype.item.item import get_item_defaults

class LotNumberGeneration(Document):
    pass
@frappe.whitelist()
def set_and_create_main_lot(doc, method=None):
    def set_existing_main_lot(item):
        if not item.lot_no:
            lot_no = frappe.db.exists(
                    "Lot Number",
                    {"item": item.part_number,"supplier": doc.supplier,"reference_doctype": doc.doctype,"reference_name": doc.name,"type":"Parent","packet":item.packet},
                )
            item.lot_no = lot_no

    get_main_lot_in_previous_items = compose(
        lambda x: x.get("lot_no"),
        excepts(StopIteration, first, lambda _: {}),
        lambda x: filter(
            lambda item: item.idx < x.idx
            and item.part_number == x.part_number,
            doc.lot_no_generate_item,
        ),
    )

    def create_new_main_lot(item):
        # warehouse = "t_warehouse" if doc.doctype == "Stock Entry" else "warehouse"
        for item in doc.lot_no_generate_item:
           
            lot_in_items = get_main_lot_in_previous_items(item)
            if lot_in_items:
                item.lot_no = lot_in_items
                return
            for item in doc.lot_no_generate_item:
                lot = frappe.get_doc(
                    {
                    "doctype": "Lot Number",
                    "naming_series":"ELOT",
                    "item": item.part_number,
                    "supplier": doc.supplier,
                    "lot_qty": item.qty,
                    "reference_doctype": doc.doctype,
                    "reference_name": doc.name or "",
                    # "purchase_order":doc.purchase_order or " ",
                    "packet":item.packet,
                    "type":"Parent"
                    }
                ).insert()
                item.lot_no = lot.name
        doc.save(ignore_permissions = True)

    if doc._action == "save":
        for item in doc.lot_no_generate_item:
            if not item.lot_no :
                set_existing_main_lot(item)

        # TODO: when `before_validate` gets merged into master create_new_batch should
        # run when doc._action == 'submit'.
        # also update `hooks.py` to use `before_validate` instead of the current
        # `before_save` method
        for item in doc.lot_no_generate_item:
            if not item.lot_no :
                create_new_main_lot(item)
    
@frappe.whitelist()
def before_validate(doc, method):
    set_and_create_main_lot(doc, method)
    set_and_create_batch(doc, method)

##Batch
@frappe.whitelist()
def set_and_create_batch(doc, method):
    def delete_existing_batch():
        docname=doc.name
        lot = frappe.get_doc({"doctype" : "Lot Number", "reference_name" : doc.name,"type":"Child"})
        # frappe.db.sql('DELETE FROM `tabLot Number` where reference_doctype = "GRN Inward" and reference_name = %s and type = "Child"',docname)
        frappe.delete_doc('Lot Number', "lot")
    def set_existing_batch(item):
        if not item.batch_no:
            has_batch_no, has_expiry_date = frappe.db.get_value(
                "Item", item.part_number, ["has_batch_no", "has_expiry_date"]
            )
            # if has_batch_no:
            batch_no = frappe.db.exists(
                    "Lot Number",
                    {"item": item.part_number,"supplier": doc.supplier,"reference_doctype": doc.doctype,"reference_name": doc.name,"type":"Child","packet":item.idx},
                )
            item.batch_no = batch_no
            item.save()

    get_batch_in_previous_items = compose(
        lambda x: x.get("batch_no"),
        excepts(StopIteration, first, lambda _: {}),
        lambda x: filter(
            lambda item: item.idx < x.idx
            and item.part_number == x.part_number ,
            doc.lot_no_generate_item_details,
        ),
    )

    def create_new_batch(item):
        # warehouse = "t_warehouse" if doc.doctype == "Stock Entry" else "warehouse"
        for item in doc.lot_no_generate_item_details:
            if not item.batch_no:
                has_batch_no, create_new_batch = frappe.db.get_value(
                "Item",
                item.part_number,
                ["has_batch_no", "create_new_batch"],
                )
                # if has_batch_no:
                # batch_in_items = get_batch_in_previous_items(item)
                # if batch_in_items:
                #     item.batch_no = batch_in_items
                #     return
                for item in doc.lot_no_generate_item_details:
                    batch = frappe.get_doc(
                    {
                    "doctype": "Lot Number",
                    "naming_series":"parent_lot.-.##",
                    "parent_lot":frappe.db.get_value("Lot Number Generation Item", {"parent": doc.name, "part_number": item.part_number}, "lot_no"),
                    "item": item.part_number,
                    "supplier": doc.supplier,
                    "lot_qty": item.qty,
                    "reference_doctype": doc.doctype,
                    "reference_name": doc.name or "",
                    # "purchase_order":doc.purchase_order or " ",
                    "packet":item.packet,
                    "type":"Child"
                    }
                    ).insert()
                    item.batch_no = batch.name
                    item.lot_no = batch.parent_lot
                doc.save(ignore_permissions = True)
    def update_lot(item):
        for item in doc.lot_no_generate_item_details:
            if item.batch_no :
                lot = frappe.get_doc('Lot Number', item.batch_no)
   
                lot.lot_qty = item.qty
                lot.save(ignore_permissions=True)
                frappe.db.commit()

    if doc._action == "save":
        # delete_existing_batch()
        for item in doc.lot_no_generate_item_details:
            if not item.batch_no :
                set_existing_batch(item)
            else :
                update_lot(item)

        # TODO: when `before_validate` gets merged into master create_new_batch should
        # run when doc._action == 'submit'.
        # also update `hooks.py` to use `before_validate` instead of the current
        # `before_save` method
        for item in doc.lot_no_generate_item_details:
            if not item.batch_no :
                create_new_batch(item)
                
@frappe.whitelist()
def after_validate(doc, method):
    set_and_create_batch(doc, method)

def create_lot_stock_entry(doc, handler=""):
    s_warehouse = frappe.db.get_value("Lot Generation Warehouse", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "from_warehouse")
    t_warehouse = frappe.db.get_value("Lot Generation Warehouse", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "to_warehouse")
    accepted_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "quality_inspection_warehouse")
    expense_account = frappe.db.get_value("Company", {"name":doc.company}, "stock_adjustment_account")
    cost_center = frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
    # try:
    se = frappe.new_doc("Stock Entry")
    se.update({ "purpose": "Repack" , "stock_entry_type": "Repack","company":doc.company})
            # if se_item.accepted_qty:
            # items=[]
    for item in doc.lot_no_generate_item:
        po_rate = frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate')
        # print("///////////",po_rate)
        valuation_rate=frappe.get_all('Stock Ledger Entry', filters={'item_code':item.part_number,'valuation_rate' : ['>', '0'],'is_cancelled':0}, fields=['valuation_rate'],limit =1)
        # print("///////////",valuation_rate)
        item_price_rate = frappe.db.get_value('Item Price', {'item_code':item.part_number,'price_list':"Standard Buying"}, 'price_list_rate')
        item_bin_rate = frappe.db.get_value('Bin', {'item_code':item.part_number,'warehouse':s_warehouse}, 'valuation_rate')
        item_val_rate = frappe.db.get_value('Item', {'item_code':item.part_number}, 'valuation_rate')
        base_rate = item_bin_rate or item_val_rate or valuation_rate[0].valuation_rate or item.last_purchase_rate or 0.00
        if item.lot_no:
            se.append("items", 
                { "item_code":item.part_number,
                "qty": item.qty,
                "s_warehouse": s_warehouse,
                "t_warehouse": "",
                "transfer_qty" : item.qty,
                "uom" : item.uom,
                "set_basic_rate_manually":0,
                # "basic_rate" : frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':item.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
                # "valuation_rate" : frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':item.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
                "basic_rate" : base_rate,
                "valuation_rate" :base_rate,
                "basic_amount" : base_rate*item.qty,
                "amount" :base_rate*item.qty,
                "conversion_factor": 1,
                "allow_zero_valuation_rate":0,
                # "reference_purchase_receipt":doc.purchase_receipt,
                "lot_number":item.lot_no,
                "expense_account":expense_account,
                "cost_center":cost_center
            })
    for se_item in doc.lot_no_generate_item_details:
        po_rate = frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate')
        item_price_rate = frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate')
        valuation_rate=frappe.get_all('Stock Ledger Entry', filters={'item_code':se_item.part_number,'valuation_rate' : ['>', '0'],'is_cancelled':0}, fields=['valuation_rate'],limit =1)
        item_bin_rate = frappe.db.get_value('Bin', {'item_code':se_item.part_number,'warehouse':s_warehouse}, 'valuation_rate')
        item_val_rate = frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'valuation_rate')
        base_rate = item_bin_rate or item_val_rate or valuation_rate[0].valuation_rate or item.last_purchase_rate or 0.00
        if se_item.batch_no:
            se.append("items", 
            { "item_code":se_item.part_number,
                "qty": se_item.qty,
                "s_warehouse": "",
                "t_warehouse": t_warehouse,
                "transfer_qty" : se_item.qty,
                "uom" : item.uom,
                "set_basic_rate_manually":0,
                # "basic_rate" : frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate') or frappe.db.get_value('Item Price', {'item_code':se_item.part_number,'price_list':"Standard Buying"}, 'price_list_rate') or 0,
                "basic_rate" : base_rate,
                "valuation_rate" :base_rate,
                "basic_amount" : base_rate*se_item.qty,
                "amount" :base_rate*se_item.qty,
                "conversion_factor": 1,
                "allow_zero_valuation_rate":0,
                # "reference_purchase_receipt":doc.purchase_receipt,
                "lot_number":se_item.batch_no,
                "expense_account":expense_account,
                "cost_center":cost_center
            })
            
    se.flags.ignore_mandatory = True
    se.set_missing_values()
    se.docstatus=1
    se.insert(ignore_permissions=True)
    doc.stock_entry =se.name
    doc.save(ignore_permissions=True)
    # except Exception as e:
    #     return {"error":e} 