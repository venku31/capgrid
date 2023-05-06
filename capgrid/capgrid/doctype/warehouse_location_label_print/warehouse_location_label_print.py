# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WarehouseLocationLabelPrint(Document):
	pass

@frappe.whitelist()
def get_locations(company,warehouse):
    fields = frappe.db.sql("""Select name,warehouse,company,main_warehouse from `tabWarehouse Location` where company=%(company)s and warehouse=%(warehouse)s""",{"company":company,"warehouse":warehouse}, as_dict=1)
    return fields
