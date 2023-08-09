from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

@frappe.whitelist(allow_guest=True)
def so_item_price(item_code):
    if item_code:
        rate=frappe.get_all('Sales Order Item', filters={'item_code':item_code,'docstatus':1}, fields=['rate'],order_by='creation desc',limit =1)
        # frappe.msgprint(str(rate))
        return rate