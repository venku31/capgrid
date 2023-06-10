
import frappe
from frappe import _

@frappe.whitelist()
def validate_warehouse(doc,method=None):
    for row in doc.items:
        warehouse = frappe.db.sql(
				""" Select warehouse from 
        (select inward_warehouse as warehouse from `tabWMS Settings details` 
        UNION
        select rejected_warehouse as warehouse from `tabWMS Settings details`
        UNION
        select hold_warehouse as warehouse from `tabWMS Settings details`)a
        where a.warehouse=%s """,row.warehouse,	as_list=1,)
        # print("//////",warehouse)
        if warehouse :
            frappe.throw(_("Row {0},Item {1}: Warehouse should not belong to Inward/Hold/Rejected").format(row.idx,row.item_code), title=_("Invalid Warehouse"))