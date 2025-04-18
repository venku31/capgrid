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
    pr.supplier_address = frappe.db.get_value('Purchase Order', {'name':doc.purchase_order}, 'supplier_address')
    pr.tax_category = frappe.db.get_value('Purchase Order', {'name':doc.purchase_order}, 'tax_category')
    pr.taxes_and_charges = frappe.db.get_value('Purchase Order', {'name':doc.purchase_order}, 'taxes_and_charges')
        # pr.supplier_address:""
            
    for item in doc.grn_inward_item:
            # if doc.purchase_order:
        po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':item.part_number,'uom':item.uom,'parent':doc.purchase_order}, 'rate')
        last_rate = frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate')
        item_price_rate = frappe.db.get_value('Item Price', {'item_code':item.part_number,'uom':item.uom,'price_list':"Standard Buying"}, 'price_list_rate')
        pr.append("items", 
            { "item_code":item.part_number,
            "qty": item.qty,
            "received_qty":item.qty,
            "uom":item.uom,
            "warehouse": frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "inward_warehouse"),
            "accepted_qty" : item.qty,
            "conversion_factor": 1,
            # "rate": po_rate or last_rate or item_price_rate or 0,
            "rate":item.rate or item_price_rate,
            "allow_zero_valuation_rate":0,
            "purchase_order":doc.purchase_order or '',
            "purchase_order_item":item.po_item or '',
            "lot_number":item.lot_no,
            "expense_account": frappe.db.get_value("Company", {"name": doc.company}, "default_expense_account"),
            "cost_center": frappe.db.get_value("Company", {"name": doc.company}, "cost_center"),
        })
    po_taxes = frappe.db.sql(""" select a.charge_type, a.row_id, a.account_head, a.description, a.rate, a.account_currency,a.cost_center from `tabPurchase Taxes and Charges` a 
    where a.parent = '{name}' """.format(name=doc.purchase_order), as_dict=1) 
    for x in po_taxes:
            taxes = pr.append("taxes", {})
            taxes.charge_type = x.charge_type
            taxes.row_id = x.row_id
            taxes.account_head = x.account_head
            taxes.description = x.description
            taxes.cost_center = x.cost_center               
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
    # update_received_qty(pr.name)
    update_parent_lot(doc)

#Main Lot
@frappe.whitelist()
def update_received_qty(pr_name):
    pr_doc= frappe.get_doc("Purchase Receipt", pr_name)
    for pr_i in pr_doc.items:
        if pr_i.get('purchase_order'):
            po = frappe.get_doc("Purchase Order", pr_i.get('purchase_order'))
            for po_i in po.items:
                if pr_i.item_code == po_i.item_code and po_i.parent == pr_i.purchase_order:
                    received_qty = po_i.received_qty + pr_i.qty
                    frappe.db.sql("update `tabPurchase Order Item` set received_qty = {0} \
                        where name = '{1}'".format(received_qty, po_i.name))
                    # if po_i.qty >= received_qty:
                    #     po_status = "To Bill"
                    #     frappe.db.sql("update `tabPurchase Order` set status = '{0}' \
                    #     where name = '{1}'".format(po_status, po_i.name))


    # po_nos = frappe.db.get_all("Purchase Receipt Item", { "parent": pr_doc.name }, "purchase_order as po")

    # for po in po_nos:
    #     if po.get('po'):
    #         po = frappe.get_doc("Purchase Order", po.get('po'))
    #         all_received = True
    #         for i in po.items:
    #             if i.qty >= i.received_qty:
    #                 all_received = False
    #         # po_status = "To Bill" if all_received else "To Receive and Bill"
    #         po_status = "To Bill"
    #         frappe.db.sql("update `tabPurchase Order` set status = '{0}' \
    #             where name = '{1}'".format(po_status, po.name))

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
                    {"idx_no": item.idx,"supplier": doc.supplier,"reference_doctype": doc.doctype,"reference_name": doc.name,"type":"Parent"},
                )
            item.lot_no = lot_no
            item.save()

    get_main_lot_in_previous_items = compose(
        lambda x: x.get("lot_no"),
        excepts(StopIteration, first, lambda _: {}),
        lambda x: filter(
            lambda item: item.idx < x.idx
            and item.idx == x.idx,
            doc.grn_inward_item,
        ),
    )

    def create_new_main_lot(item):
        # warehouse = "t_warehouse" if doc.doctype == "Stock Entry" else "warehouse"
        for item in doc.grn_inward_item:
            if not item.lot_no:
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
                    if not item.lot_no:
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
                        "type":"Parent",
                        "idx_no":item.idx
                        }
                        ).insert()
                        item.lot_no = lot.name
                        frappe.db.sql("""UPDATE `tabGRN Inward Item` set lot_no=%(lot_no)s
                where parent=%(name)s and part_number=%(part_number)s""",{"lot_no":lot.name,"name":doc.name,"part_number":item.part_number})
                doc.save(ignore_permissions = True)
    def update_main_lot(item):
        for item in doc.grn_inward_item:
            if item.lot_no :
                lot = frappe.get_doc('Lot Number', item.lot_no)
                if lot.lot_qty != item.qty :
                    lot.lot_qty = item.qty
                    # lot.reference_doctype = doc.doctype
                    # lot.reference_name = doc.name
                    lot.save(ignore_permissions=True)
                    frappe.db.commit()
                    

    if doc._action == "save":
        for item in doc.grn_inward_item:
            if not item.lot_no :
                set_existing_main_lot(item)
            else :
                update_main_lot(item)

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
    # set_or_create_batch(doc, method)

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
                    {"idx_no": item.idx,"supplier": doc.supplier,"reference_doctype": doc.doctype,"reference_name": doc.name,"type":"Child"},
                )
            item.batch_no = batch_no
            item.save()

    get_batch_in_previous_items = compose(
        lambda x: x.get("batch_no"),
        excepts(StopIteration, first, lambda _: {}),
        lambda x: filter(
            lambda item: item.idx < x.idx
            and item.idx == x.idx,
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
                # for item in doc.grn_inward_item_details:
                batch = frappe.get_doc(
                {
                "doctype": "Lot Number",
                "naming_series":"parent_lot.-.##",
                "parent_lot":frappe.db.get_value("GRN Inward Item", {"parent": doc.name, "part_number": item.part_number,"idx":item.parent_idx}, "lot_no"),
                "item": item.part_number,
                "supplier": doc.supplier,
                "lot_qty": item.qty,
                "reference_doctype": doc.doctype,
                "reference_name": doc.name or "",
                # "purchase_order":doc.purchase_order or " ",
                "packet":item.packet,
                "idx_no":item.idx,
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
            # else :
            #     update_lot(item)

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
        return frappe.db.sql(""" select item_code,item_name,parent,qty,stock_uom,name from `tabPurchase Order Item`
        where parent = %(parent)s and (qty-received_qty)>0 and item_name like %(txt)s
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
            po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':item.part_number,'parent':doc.purchase_order}, 'rate')
            last_rate = frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate')
            item_price_rate = frappe.db.get_value('Item Price', {'item_code':item.part_number,'price_list':"Standard Buying"}, 'price_list_rate')
            item_bin_rate = frappe.db.get_value('Bin', {'item_code':item.part_number,'warehouse':s_warehouse}, 'valuation_rate')
            item_val_rate = frappe.db.get_value('Item', {'item_code':item.part_number}, 'valuation_rate')
            base_rate = item_bin_rate or po_rate or item_val_rate or last_rate or 0.00
            if item.lot_no:
                se.append("items", 
                { "item_code":item.part_number,
                "qty": item.qty,
                "s_warehouse": s_warehouse,
                "t_warehouse": "",
                "transfer_qty" : item.qty,
                "uom" : item.uom,
                "set_basic_rate_manually":0,
                "basic_rate" : base_rate ,#frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate'),
                "valuation_rate" : base_rate ,#frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate'),
                "basic_amount" :item.qty*base_rate,#frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate'),
                "amount" :item.qty*base_rate,#frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate'),
                "conversion_factor": 1,
                "allow_zero_valuation_rate":0,
                "reference_purchase_receipt":doc.purchase_receipt,
                "lot_number":item.lot_no,
                "expense_account":expense_account,
                "cost_center":cost_center
                })
        for se_item in doc.grn_inward_item_details:
            po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':item.part_number,'parent':doc.purchase_order}, 'rate')
            last_rate = frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate')
            item_price_rate = frappe.db.get_value('Item Price', {'item_code':item.part_number,'price_list':"Standard Buying"}, 'price_list_rate')
            item_bin_rate = frappe.db.get_value('Bin', {'item_code':item.part_number,'warehouse':s_warehouse}, 'valuation_rate')
            item_val_rate = frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'valuation_rate')
            base_rate = item_bin_rate or po_rate or item_val_rate or last_rate or 0.00
            if se_item.batch_no:
                se.append("items", 
                { "item_code":se_item.part_number,
                "qty": se_item.qty,
                "s_warehouse": "",
                "t_warehouse": t_warehouse,
                "is_finished_item":1,
                "transfer_qty" : se_item.qty,
                "uom" : item.uom,
                "set_basic_rate_manually":0,
                "basic_rate" :base_rate, #frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate'),
                "valuation_rate" :base_rate, #frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate'),
                "basic_amount" :se_item.qty*base_rate, #frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate'),
                "amount" :se_item.qty*base_rate, #frappe.db.get_value('Item', {'item_code':se_item.part_number}, 'last_purchase_rate'),
                "conversion_factor": 1,
                "allow_zero_valuation_rate":0,
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

@frappe.whitelist()
def create_new_batches(grn,product_description,supplier):
        # warehouse = "t_warehouse" if doc.doctype == "Stock Entry" else "warehouse"
        product = json.loads(product_description)
        for item in product:
                batch = frappe.get_doc(
                {
                "doctype": "Lot Number",
                "parent_lot":frappe.db.get_value("GRN Inward Item", {"parent": grn, "part_number": item["part_number"]}, "lot_no"),
                "naming_series":"parent_lot.-.##",
                "item": item["part_number"],
                "supplier": supplier,
                "lot_qty": item["qty"],
                "reference_doctype": "GRN Inward",
                "reference_name": grn,
                # "purchase_order":doc.purchase_order or " ",
                "packet":item["packet"],
                "type":"Child"
                }
                ).insert()
                # item.batch_no = batch.name
                # item.lot_no = batch.parent_lot
        return batch.name

@frappe.whitelist()
def get_po_details(po,part_number):
    return frappe.get_all(
        "Purchase Order Item", filters={"docstatus": 1,"parent":po,"item_code":part_number}, fields=["item_code", "qty","received_qty","uom","rate","name"]
    )
@frappe.whitelist()
def update_parent_lot(doc):
        for item in doc.grn_inward_item_details:
            if item.batch_no and not item.lot_no :
                item.lot_no = frappe.db.get_value("Lot Number", {"name": item.batch_no}, "parent_lot")
        doc.save(ignore_permissions=True)
        frappe.db.commit()

@frappe.whitelist()
def delete_lot(doc,part_number,parent_lot):
#         child_lots = frappe.db.sql(
#         """
#         SELECT batch_no from `tabGRN Inward Item Details`
# where parent=%(doc)s and part_number=%(part_number)s """, values={"doc":doc,"part_number":part_number},as_dict=1,)
#         for lots in child_lots:
#             lot_doc = frappe.get_value("Lot Number",lots.batch_no)
#             if lot_doc :
#                 # lot_doc.flags.ignore_links = True
#                 frappe.delete_doc("Lot Number",lot_doc)
#                 frappe.db.commit()
#         parent_lot_doc = frappe.get_value("Lot Number",parent_lot)
#         if parent_lot_doc :
#             # parent_lot_doc.flags.ignore_links = True
#             frappe.delete_doc("Lot Number",parent_lot_doc)
#             frappe.db.commit()
    if part_number :
        frappe.db.sql(""" DELETE FROM `tabLot Number` where reference_name = %(doc)s and parent_lot=%(parent_lot)s and item=%(part_number)s
                  """,{ 'doc':doc,'parent_lot': parent_lot, 'part_number': part_number })
        frappe.db.sql(""" DELETE FROM `tabLot Number` where reference_name = %(doc)s and name=%(parent_lot)s and item=%(part_number)s
                  """,{ 'doc':doc,'parent_lot': parent_lot, 'part_number': part_number })
