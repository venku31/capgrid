# Copyright (c) 2023, Capgrid Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.core.doctype.data_import.importer import ImportFile

class PickListUpload(Document):
	def on_submit(self):
		if self.import_file:
			data = ImportFile('PickList',self.import_file)
			data.raw_data.pop(0)
			final_data = data.raw_data
			items = []
			# for d in final_data:
			# 	items.append({'part_number': d[1],'warehouse':d[0], 'plant_code': d[2],
		  	# 		'trigger_qty': d[3],'reason': d[4], 'remarks': d[5]})
			for d in final_data:
				items.append({'part_number': d[0], 'plant_code': d[1],
		  			'trigger_qty': d[2]})
			# frappe.get_doc({'doctype':'PickList','customer': self.customer,'date': frappe.utils.today(),
		   	# 		'warehouse': final_data[0][0],'details': items}).submit()
			cust_shrt = "".join(segment.strip() for segment in self.customer_name.split("."))
			# customer_short=self.customer_name.replace(' ','')[0:6]
			customer_short=cust_shrt.replace(' ','')[0:6]
			frappe.get_doc({'doctype':'PickList','customer': self.customer,"customer_short":customer_short,'date': frappe.utils.today(),
		   		'warehouse': self.warehouse,'details': items}).save()
				

