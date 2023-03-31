# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

#import frappe
from frappe.model.document import Document

class LotNumber(Document):
	pass
# import frappe
# from frappe import _
# from frappe.model.document import Document
# from frappe.model.naming import make_autoname

# # Autoname the series According To Branch
# def autoname(doc, method):
#     if doc.parent_lot:
#         doc.name = make_autoname(doc.parent_lot+"-.##")
#         return doc.name
#     elif not doc.parent_lot:
#         doc.name = make_autoname("LOT"+".####")
#         return doc.name
#     else :
#         return doc.name