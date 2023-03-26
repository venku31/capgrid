# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, add_months, today, add_days, nowdate,formatdate
import json
from toolz import excepts, first, compose
from frappe.model.db_query import DatabaseQuery
from frappe.desk.reportview import get_match_cond, get_filters_cond
class InwardGRN(Document):
    pass
@frappe.whitelist()
def create_pr(company,supplier,product_description,bill_no,bill_date):
    # set_or_create_batch(doc, method)
    
    pr = frappe.new_doc("Purchase Receipt")
    pr.company = company
    pr.supplier = supplier
    pr.posting_date = today()
    pr.supplier_delivery_note = bill_no
    pr.supplier_invoice_date = bill_date
    product = json.loads(product_description)
    
    for i in product:
        if not 'batch_no' in i:
            raise AttributeError('Generate Batch')
        else:
            # print('ok')
            pr.append("items", {
            "item_code": i["part_number"],
            "qty": i["qty"],
            "batch_no": i["batch_no"],
            })
            pr.save(ignore_permissions = True)
    return pr.name
##Batch
@frappe.whitelist()
def set_or_create_batch(doc, method):
    def set_existing_batch(item):
        if not item.batch_no:
            has_batch_no, has_expiry_date = frappe.db.get_value(
                "Item", item.part_number, ["has_batch_no", "has_expiry_date"]
            )
            if has_batch_no:
                batch_no = frappe.db.exists(
                    "Batch",
                    {"item": item.part_number,"supplier": doc.supplier,"reference_doctype": doc.doctype,"reference_name": doc.name,"purchase_order":doc.purchase_order,"packet":item.packet},
                )
                item.batch_no = batch_no

    get_batch_in_previous_items = compose(
        lambda x: x.get("batch_no"),
        excepts(StopIteration, first, lambda _: {}),
        lambda x: filter(
            lambda item: item.idx < x.idx
            and item.part_number == x.part_number,
            doc.inward_grn_item_details,
        ),
    )

    def create_new_batch(item):
        # warehouse = "t_warehouse" if doc.doctype == "Stock Entry" else "warehouse"
        for item in doc.inward_grn_item_details:
            if not item.batch_no:
                has_batch_no, create_new_batch = frappe.db.get_value(
                "Item",
                item.part_number,
                ["has_batch_no", "create_new_batch"],
                )
                if has_batch_no:
                    batch_in_items = get_batch_in_previous_items(item)
                    if batch_in_items:
                        item.batch_no = batch_in_items
                        return
                    for item in doc.inward_grn_item_details:
                        batch = frappe.get_doc(
                        {
                        "doctype": "Batch",
                        "item": item.part_number,
                        "supplier": doc.supplier,
                        "batch_qty": item.qty,
                        "reference_doctype": doc.doctype,
                        "reference_name": doc.name or "",
                        "purchase_order":doc.purchase_order or " ",
                        "packet":item.packet
                        }
                        ).insert()
                        item.batch_no = batch.name
                    doc.save(ignore_permissions = True)

    if doc._action == "save":
        for item in doc.inward_grn_item_details:
            if not item.batch_no :
                set_existing_batch(item)

        # TODO: when `before_validate` gets merged into master create_new_batch should
        # run when doc._action == 'submit'.
        # also update `hooks.py` to use `before_validate` instead of the current
        # `before_save` method
        for item in doc.inward_grn_item_details:
            if not item.batch_no :
                create_new_batch(item)

@frappe.whitelist()
def before_validate(doc, method):
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
	return frappe.db.sql(""" select item_code,item_name,parent,qty,stock_uom from `tabPurchase Order Item`
		where parent = %(parent)s and item_name like %(txt)s
		limit %(start)s, %(page_len)s""", {
			'parent': filters.get("parent"),
			'start': start,
			'page_len': page_len,
			'txt': "%%%s%%" % txt
		})