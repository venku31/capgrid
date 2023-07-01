# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PickListScreen(Document):
	def on_update(self):
		if self.action == 'Start Picking':
			pick_doc = frappe.get_doc('PickList', self.pick_list)
			if pick_doc.get('details'):
				# for item in pick_doc.get('details'):
				part_number = frappe.db.get_value('PickList Details',{"parent":self.pick_list,'idx':1},'part_number')
				frappe.get_doc({'doctype': 'Picking List','picklist': pick_doc.name, 
		     					'date': frappe.utils.today(),'warehouse': pick_doc.warehouse, 
								'company': pick_doc.company, 'customer': pick_doc.customer,'total_qty': pick_doc.total_qty,
								'part_number': part_number
							}).insert()
