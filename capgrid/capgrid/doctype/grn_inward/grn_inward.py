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
def create_pr(company,supplier,product_description,bill_no,bill_date):
    # set_or_create_batch(doc, method)
    
    pr = frappe.new_doc("Purchase Receipt")
    pr.company = company
    pr.supplier = supplier
    pr.posting_date = today()
    pr.supplier_delivery_note = bill_no
    pr.supplier_invoice_date = bill_date
    pr.supplier_address = "",
    product = json.loads(product_description)
    
    for i in product:
        if not 'lot_no' in i:
            raise AttributeError('Generate Batch')
        else:
            # print('ok')
            pr.append("items", {
            "item_code": i["part_number"],
            # "warehouse":frappe.db.get_value("Company", {"name":company}, "default_in_transit_warehouse"),
            "warehouse": get_item_defaults(i["part_number"], company).get("default_warehouse"),
            "warehouse_location": get_item_defaults(i["part_number"], company).get("warehouse_location"),
            "qty": i["qty"],
            "lot_number": i["lot_no"],
            })
            pr.flags.ignore_mandatory = True
            pr.save(ignore_permissions = True)
    return pr.name
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
    def set_existing_batch(item):
        if not item.batch_no:
            has_batch_no, has_expiry_date = frappe.db.get_value(
                "Item", item.part_number, ["has_batch_no", "has_expiry_date"]
            )
            # if has_batch_no:
            batch_no = frappe.db.exists(
                    "Lot Number",
                    {"item": item.part_number,"supplier": doc.supplier,"reference_doctype": doc.doctype,"reference_name": doc.name,"type":"Child","packet":item.packet},
                )
            item.batch_no = batch_no
            item.save()

    get_batch_in_previous_items = compose(
        lambda x: x.get("batch_no"),
        excepts(StopIteration, first, lambda _: {}),
        lambda x: filter(
            lambda item: item.idx < x.idx
            and item.part_number == x.part_number,
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
                batch_in_items = get_batch_in_previous_items(item)
                if batch_in_items:
                    item.batch_no = batch_in_items
                    return
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
                doc.save(ignore_permissions = True)

    if doc._action == "save":
        for item in doc.grn_inward_item_details:
            if not item.batch_no :
                set_existing_batch(item)

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