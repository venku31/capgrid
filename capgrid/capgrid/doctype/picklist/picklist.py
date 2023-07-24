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
    
    def on_update(self):
        # frappe.get_doc({'doctype':'PickList Screen','customer': self.customer, 'pick_list': self.name
        #                 }).insert()
        exists = frappe.db.get_value('Picking List',{"picklist":self.name},'name')
        if not exists :
            part_number = frappe.db.get_value('PickList Details',{"parent":self.name,'idx':1},'part_number')
            frappe.get_doc({'doctype': 'Picking List','picklist': self.name,'date': frappe.utils.today(),'warehouse': self.warehouse, 
                        'company': self.company, 'customer': self.customer,'total_qty': self.total_qty,'part_number': part_number
            }).insert()

    def on_submit(doc,handler=""):
        # warehouse = frappe.db.get_value("WMS Settings details", {"company":doc.company,"main_warehouse":doc.main_warehouse}, "inward_warehouse")
        expense_account = frappe.db.get_value("Company", {"name":doc.company}, "default_expense_account")
        cost_center = frappe.db.get_value("Company", {"name":doc.company}, "cost_center")
        # try:
        si_doc = frappe.new_doc("Sales Invoice")
    # pr.update({ "company": doc.company , "supplier": doc.supplier,"posting_date":today(),"supplier_delivery_note":doc.bill_no,"supplier_invoice_date":doc.bill_date,"supplier_address":""})
        si_doc.customer = doc.customer
        si_doc.posting_date = frappe.utils.today()
        # si_doc.supplier_delivery_note = doc.supplier_invoice_no
        # si_doc.supplier_invoice_date = doc.supplier_invoice_date
        si_doc.company = doc.company
        # pr.supplier_address:""
            
        for item in doc.details:
            # if doc.purchase_order:
            # po_rate = frappe.db.get_value('Purchase Order Item', {'item_code':item.part_number,'uom':item.uom,'parent':doc.purchase_order}, 'rate')
            # last_rate = frappe.db.get_value('Item', {'item_code':item.part_number}, 'last_purchase_rate')
            # item_price_rate = frappe.db.get_value('Item Price', {'item_code':item.part_number,'uom':item.uom,'price_list':"Standard Buying"}, 'price_list_rate')
            si_doc.append("items", 
            { "item_code":item.part_number,
            "qty": item.total_picked_qty,
            # "uom":item.uom,
            "warehouse": doc.warehouse,
            "conversion_factor": 1,
            "rate":item.price,
            "allow_zero_valuation_rate":1,
            "sales_order":doc.sales_order or '',
            # "lot_number":item.lot_no,
            # "expense_account": frappe.db.get_value("Company", {"name": doc.company}, "default_expense_account"),
            # "cost_center": frappe.db.get_value("Company", {"name": doc.company}, "cost_center"),
        })
                    
        si_doc.flags.ignore_mandatory = True
        si_doc.set_missing_values()
        si_doc.docstatus=1
        si_doc.insert(ignore_permissions=True)
        # pr.save(ignore_permissions = True)
        # pr.submit()
        doc.sales_invoice =si_doc.name
        doc.save(ignore_permissions=True)


@frappe.whitelist()
def get_actual_stock(warehouse,part_number):
    if part_number:
        actual_qty=frappe.db.sql(""" select sum(actual_qty) as actual_qty from tabBin where item_code=%(part_number)s and warehouse=%(warehouse)s """,{"part_number":part_number,"warehouse":warehouse} , as_dict=1)
        return actual_qty[0].actual_qty
    
@frappe.whitelist()
def sales_order_price(sales_order,part_number):
    if sales_order:
        rate=frappe.get_all('Sales Order Item', filters={'parent':sales_order,'item_code':part_number}, fields=['rate','item_tax_template'],limit =1)
        # frappe.msgprint(str(rate))
        print("/////////",rate)
        return rate

        