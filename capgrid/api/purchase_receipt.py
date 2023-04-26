import frappe



@frappe.whitelist()
def get_purchase_receipt_po(purchase_order=None):
    if purchase_order:
        return frappe.db.sql(f""" SELECT distinct pritem.purchase_order,pr.name as purchase_receipt from `tabPurchase Receipt` pr LEFT JOIN `tabPurchase Receipt Item` pritem ON(pr.name=pritem.parent)
        where pr.docstatus=1 and pritem.purchase_order='%(purchase_order)s' """ %{"purchase_order": purchase_order}, as_dict=True)
    else :
        return frappe.db.sql(f""" SELECT distinct pr.name as purchase_receipt,pritem.purchase_order from `tabPurchase Receipt` pr LEFT JOIN `tabPurchase Receipt Item` pritem ON(pr.name=pritem.parent)
        where pr.docstatus=1  """ , as_dict=True)
# def get_purchase_receipt_po():
#     return frappe.db.sql(f""" SELECT distinct pr.name as purchase_receipt,pritem.purchase_order from `tabPurchase Receipt` pr LEFT JOIN `tabPurchase Receipt Item` pritem ON(pr.name=pritem.parent)
#     where pr.docstatus=1  """ , as_dict=True)