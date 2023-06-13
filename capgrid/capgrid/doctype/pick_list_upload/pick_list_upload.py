# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PickListUpload(Document):
    pass
import frappe
from frappe import _

@frappe.whitelist()
def get_actual_stock(warehouse,part_number):
    if part_number:
        actual_qty=frappe.db.sql(""" select sum(actual_qty) as actual_qty from tabBin where item_code=%(part_number)s and warehouse=%(warehouse)s """,{"part_number":part_number,"warehouse":warehouse} , as_dict=1)
        # print("////////",actual_qty)
        return actual_qty
        