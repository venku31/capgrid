# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PickList(Document):
    def validate(self):
        self.total_qty = 0
        self.total_picked_qty = 0
        if self.get('details'):
            for item in self.get('details'):
                self.total_qty += frappe.utils.flt(item.trigger_qty) if item.trigger_qty else 0
                self.total_picked_qty += frappe.utils.flt(item.total_picked_qty) if item.total_picked_qty else 0
                item.actual_stock = get_actual_stock(self.warehouse, item.part_number)
                item.to_be_picked=item.trigger_qty
    
    def on_submit(self):
        # frappe.get_doc({'doctype':'PickList Screen','customer': self.customer, 'pick_list': self.name
        #                 }).insert()
        exists = frappe.db.get_value('Picking List',{"picklist":self.name},'name')
        if not exists :
            part_number = frappe.db.get_value('PickList Details',{"parent":self.name,'idx':1},'part_number')
            frappe.get_doc({'doctype': 'Picking List','picklist': self.name,'date': frappe.utils.today(),'warehouse': self.warehouse, 
						'company': self.company, 'customer': self.customer,'total_qty': self.total_qty,'part_number': part_number
		    }).insert()

    

@frappe.whitelist()
def get_actual_stock(warehouse,part_number):
    if part_number:
        actual_qty=frappe.db.sql(""" select sum(actual_qty) as actual_qty from tabBin where item_code=%(part_number)s and warehouse=%(warehouse)s """,{"part_number":part_number,"warehouse":warehouse} , as_dict=1)
        return actual_qty[0].actual_qty
        