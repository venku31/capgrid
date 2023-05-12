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

class GRNInward(Document):
    pass
@frappe.whitelist()
def create_pr(company,supplier,product_description,bill_no,bill_date,grn_inward,main_warehouse,purchase_order=None):
    # set_or_create_batch(doc, method)
    pr = frappe.new_doc("Purchase Receipt")
    pr.company = company
    pr.supplier = supplier
    pr.posting_date = today()
    pr.supplier_delivery_note = bill_no
    pr.supplier_invoice_date = bill_date
    pr.supplier_address = "",
    # pr.grn_inward = grn_inward
    product = json.loads(product_description)
    
    for i in product:
        if not 'lot_no' in i:
            raise AttributeError('Generate Batch')
        else:
            # print('ok')
            pr.append("items", {
            "item_code": i["part_number"],
            # "warehouse":frappe.db.get_value("Company", {"name":company}, "default_in_transit_warehouse"),
            "warehouse": frappe.db.get_value("WMS Settings details", {"company":company,"main_warehouse":main_warehouse}, "inward_warehouse") or get_item_defaults(i["part_number"], company).get("default_warehouse"),
            # "warehouse_location": get_item_defaults(i["part_number"], company).get("warehouse_location") or frappe.db.get_value("WMS Settings details", {"company":company}, "temporary_location"),
            # "warehouse_location":""
            "qty": i["qty"],
            "purchase_order":purchase_order or "",
            "lot_number": i["lot_no"],
            "expense_account": frappe.db.get_value("Company", {"name": company}, "default_expense_account"),
            "cost_center": frappe.db.get_value("Company", {"name": company}, "cost_center"),
            })
            pr.flags.ignore_mandatory = True
            pr.save(ignore_permissions = True)
            pr.submit()
    return pr.name

def create_purchase_receipt(doc,handler=""):
    warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "inward_warehouse")
    expense_account = frappe.db.get_value("Company", {"name":doc.company}, "default_expense_account")
    cost_center = frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
    # try:
    pr = frappe.new_doc("Purchase Receipt")
    # pr.update({ "company": doc.company , "supplier": doc.supplier,"posting_date":today(),"supplier_delivery_note":doc.bill_no,"supplier_invoice_date":doc.bill_date,"supplier_address":""})
    pr.supplier = doc.supplier
    pr.posting_date = frappe.utils.today()
    pr.supplier_delivery_note = doc.supplier_invoice_no
    pr.supplier_invoice_date = doc.supplier_invoice_date
    pr.company = doc.company
        # pr.supplier_address:""
            
    for item in doc.grn_inward_item:
            # if doc.purchase_order:
        po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':item.part_number,'uom':item.uom,'parent':doc.purchase_order}, 'rate')
        item_price_rate = frappe.db.get_value('Item Price', {'item_code':item.part_number,'uom':item.uom,'price_list':"Standard Buying"}, 'price_list_rate')
        pr.append("items", 
            { "item_code":item.part_number,
            "qty": item.qty,
            "received_qty":item.qty,
            "uom":item.uom,
            "warehouse": frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "inward_warehouse"),
            "accepted_qty" : item.qty,
            "conversion_factor": 1,
            "rate": po_rate or item_price_rate or 0,
            "allow_zero_valuation_rate":1,
            "purchase_order":doc.purchase_order or '',
            "lot_number":item.lot_no,
            "expense_account": frappe.db.get_value("Company", {"name": doc.company}, "default_expense_account"),
            "cost_center": frappe.db.get_value("Company", {"name": doc.company}, "cost_center"),
        })
                    
    pr.flags.ignore_mandatory = True
    pr.set_missing_values()
    pr.docstatus=1
    pr.insert(ignore_permissions=True)
        # pr.save(ignore_permissions = True)
        # pr.submit()
    doc.purchase_receipt =pr.name
    doc.save(ignore_permissions=True)
    # except Exception as e:
    #     return {"error":e} 
    # create_lot_split_entry(doc)

#Main Lot
@frappe.whitelist()
def set_or_create_main_lot(doc, method=None):
    def set_existing_main_lot(item):
        if not item.lot_no:
        #     has_batch_no, has_expiry_date = frappe.db.get_value(
        #         "Item", item.part_number, ["has_batch_no", "has_expiry_date"]
        #     )
        #     if has_batch_no:
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
            doc.grn_inward_item,
        ),
    )

    def create_new_main_lot(item):
        # warehouse = "t_warehouse" if doc.doctype == "Stock Entry" else "warehouse"
        for item in doc.grn_inward_item:
            # if not item.batch_no:
            #     has_batch_no, create_new_batch = frappe.db.get_value(
            #     "Item",
            #     item.part_number,
            #     ["has_batch_no", "create_new_batch"],
            #     )
            #     if has_batch_no:
            lot_in_items = get_main_lot_in_previous_items(item)
            if lot_in_items:
                item.lot_no = lot_in_items
                return
            for item in doc.grn_inward_item:
                lot = frappe.get_doc(
                    {
                    "doctype": "Lot Number",
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
        for item in doc.grn_inward_item:
            if not item.lot_no :
                set_existing_main_lot(item)

        # TODO: when `before_validate` gets merged into master create_new_batch should
        # run when doc._action == 'submit'.
        # also update `hooks.py` to use `before_validate` instead of the current
        # `before_save` method
        for item in doc.grn_inward_item:
            if not item.lot_no :
                create_new_main_lot(item)
    
@frappe.whitelist()
def before_validate(doc, method):
    set_or_create_main_lot(doc, method)
    set_or_create_batch(doc, method)

##Batch
@frappe.whitelist()
def set_or_create_batch(doc, method):
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
            doc.grn_inward_item_details,
        ),
    )

    def create_new_batch(item):
        # warehouse = "t_warehouse" if doc.doctype == "Stock Entry" else "warehouse"
        for item in doc.grn_inward_item_details:
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
                for item in doc.grn_inward_item_details:
                    batch = frappe.get_doc(
                    {
                    "doctype": "Lot Number",
                    "naming_series":"parent_lot.-.##",
                    "parent_lot":frappe.db.get_value("GRN Inward Item", {"parent": doc.name, "part_number": item.part_number}, "lot_no"),
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
        for item in doc.grn_inward_item_details:
            if item.batch_no :
                lot = frappe.get_doc('Lot Number', item.batch_no)
   
                lot.lot_qty = item.qty
                lot.save(ignore_permissions=True)
                frappe.db.commit()

    if doc._action == "save":
        # delete_existing_batch()
        for item in doc.grn_inward_item_details:
            if not item.batch_no :
                set_existing_batch(item)
            else :
                update_lot(item)

        # TODO: when `before_validate` gets merged into master create_new_batch should
        # run when doc._action == 'submit'.
        # also update `hooks.py` to use `before_validate` instead of the current
        # `before_save` method
        for item in doc.grn_inward_item_details:
            if not item.batch_no :
                create_new_batch(item)
                
@frappe.whitelist()
def after_validate(doc, method):
    set_or_create_batch(doc, method)


@frappe.whitelist()
# def po_item_query(doctype, txt, searchfield, start, page_len, filters):
    # conditions = []
    # return frappe.db.sql("""select `tabPurchase Order Item`.item_code,`tabPurchase Order Item`.parent,`tabPurchase Order Item`.item_name,`tabPurchase Order Item`.qty,`tabPurchase Order Item`.stock_uom
    # 	from `tabPurchase Order Item`
    # 	where `tabPurchase Order Item`.docstatus=1 and `tabPurchase Order Item`.parent = %(parent)s and `tabPurchase Order Item`.%(key)s like "%(txt)s"
    # 		%(fcond)s  %(mcond)s
    # 	limit %(start)s, %(page_len)s """ %  {'key': searchfield, 'txt': "%%%s%%" % txt,'parent': filters.get("parent"),
    # 	'fcond': get_filters_cond(doctype, filters, conditions),
    # 	'mcond':get_match_cond(doctype), 'start': start, 'page_len': page_len})
def po_item_query(doctype, txt, searchfield, start, page_len, filters):
    if filters.get("parent"):
        return frappe.db.sql(""" select item_code,item_name,parent,qty,stock_uom from `tabPurchase Order Item`
        where parent = %(parent)s and item_name like %(txt)s
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

def validate_supplier_invoice_no(self,method=None):
    if self.supplier_invoice_no:
        fiscal_year = get_fiscal_year(self.grn_date, company=self.company, as_dict=True)
        si = frappe.db.sql('''select name,supplier from `tabGRN Inward`
            where
                supplier_invoice_no = %(supplier_invoice_no)s
                and name != %(name)s
                and supplier = %(supplier)s
                and docstatus < 2
                and grn_date between %(year_start_date)s and %(year_end_date)s''', {
                    "supplier_invoice_no": self.supplier_invoice_no,
                    "name": self.name,
                    "supplier" : self.supplier,
                    "year_start_date": fiscal_year.year_start_date,
                    "year_end_date": fiscal_year.year_end_date
                })
 
        if si:
            si = si[0][0]
            frappe.throw(_("Supplier Invoice No exists in Inward {0}".format(si)))


def create_lot_split_entry(doc, handler=""):
    # if doc.scaned_location == doc.location :
    # create_purchase_receipt(doc)
    s_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "inward_warehouse")
    t_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "inward_warehouse")
    accepted_warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "quality_inspection_warehouse")
    expense_account = frappe.db.get_value("Company", {"name":doc.company}, "stock_adjustment_account")
    cost_center = frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
    try:
        se = frappe.new_doc("Stock Entry")
        se.update({ "purpose": "Repack" , "stock_entry_type": "Repack","company":doc.company})
            # if se_item.accepted_qty:
            # items=[]
        for item in doc.grn_inward_item:
            po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':item.part_number,'uom':item.uom,'parent':doc.purchase_order}, 'rate')
            item_price_rate = frappe.db.get_value('Item Price', {'item_code':item.part_number,'uom':item.uom,'price_list':"Standard Buying"}, 'price_list_rate')
            if item.lot_no:
                se.append("items", 
                { "item_code":item.part_number,
                "qty": item.qty,
                "s_warehouse": s_warehouse,
                "t_warehouse": "",
                "transfer_qty" : item.qty,
                "uom" : item.uom,
                "set_basic_rate_manually":1,
                "basic_rate" : po_rate or item_price_rate or 0,
                "conversion_factor": 1,
                "allow_zero_valuation_rate":1,
                "reference_purchase_receipt":doc.purchase_receipt,
                "lot_number":item.lot_no,
                "expense_account":expense_account,
                "cost_center":cost_center
                })
        for se_item in doc.grn_inward_item_details:
            po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':item.part_number,'uom':item.uom,'parent':doc.purchase_order}, 'rate')
            item_price_rate = frappe.db.get_value('Item Price', {'item_code':item.part_number,'uom':item.uom,'price_list':"Standard Buying"}, 'price_list_rate')
            if se_item.batch_no:
                se.append("items", 
                { "item_code":se_item.part_number,
                "qty": se_item.qty,
                "s_warehouse": "",
                "t_warehouse": t_warehouse,
                "transfer_qty" : se_item.qty,
                "uom" : item.uom,
                "set_basic_rate_manually":1,
                "basic_rate" : po_rate or item_price_rate or 0,
                "conversion_factor": 1,
                "allow_zero_valuation_rate":1,
                "reference_purchase_receipt":doc.purchase_receipt,
                "lot_number":se_item.batch_no,
                "expense_account":expense_account,
                "cost_center":cost_center
                })
            
        se.flags.ignore_mandatory = True
        se.set_missing_values()
        se.docstatus=1
        se.insert(ignore_permissions=True)
        # doc.stock_entry =se.name
        doc.save(ignore_permissions=True)
    except Exception as e:
        return {"error":e} 