from __future__ import unicode_literals
from frappe.utils import flt
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from erpnext.stock.doctype.stock_entry.stock_entry import get_warehouse_details,get_uom_details
from erpnext.stock.utils import get_incoming_rate
from erpnext.stock.stock_ledger import update_entries_after,get_valuation_rate
import frappe
import erpnext
from frappe.utils import cint, comma_or, cstr, flt
from frappe.utils import cint, comma_or, cstr, flt, format_time, formatdate, getdate, nowdate
import erpnext
from erpnext.accounts.general_ledger import process_gl_map
from erpnext.controllers.taxes_and_totals import init_landed_taxes_and_totals
from erpnext.manufacturing.doctype.bom.bom import add_additional_cost, validate_bom_no
from erpnext.setup.doctype.brand.brand import get_brand_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock.doctype.batch.batch import get_batch_no, get_batch_qty, set_batch_nos
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.stock.doctype.serial_no.serial_no import (
    get_serial_nos,
    update_serial_nos_after_submit,
)
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import (
    OpeningEntryAccountError,
)
from erpnext.stock.get_item_details import (
    get_bin_details,
    get_conversion_factor,
    get_default_cost_center,
    get_reserved_qty_for_so,
)
from erpnext.stock.stock_ledger import NegativeStockError, get_previous_sle, get_valuation_rate
from erpnext.stock.utils import get_bin, get_incoming_rate


# def validate_with_material_request(self):
#     bypass_material_request_validation = frappe.get_value("Company", self.company,"bypass_material_request_validation") or 0
#     if bypass_material_request_validation:
#         return
#     for item in self.get("items"):
#         if item.material_request:
#             mreq_item = frappe.db.get_value("Material Request Item",
#                 {"name": item.material_request_item, "parent": item.material_request},
#                 ["item_code", "warehouse", "idx"], as_dict=True)
#             if mreq_item.item_code != item.item_code or \
#             mreq_item.warehouse != (item.s_warehouse if self.purpose== "Material Issue" else item.t_warehouse):
#                 frappe.throw(_("Item or Warehouse for row {0} does not match Material Request").format(item.idx),
#                     frappe.MappingMismatchError)


# def validate_with_material_request_override(doc, method):
#     StockEntry.validate_with_material_request = validate_with_material_request

# def set_rate_for_outgoing_items(self, reset_outgoing_rate=True, raise_error_if_no_rate=True):
# 		outgoing_items_cost = 0.0
# 		for d in self.get("items"):
# 			if d.s_warehouse and not d.set_basic_rate_manually:
# 				if reset_outgoing_rate:
# 					args = self.get_args_for_incoming_rate(d)
# 					rate = get_incoming_rate(args, raise_error_if_no_rate)
# 					if rate > 0:
# 						d.basic_rate = rate

# 				d.basic_amount = flt(flt(d.transfer_qty) * flt(d.basic_rate), d.precision("basic_amount"))
# 				if not d.t_warehouse:
# 					outgoing_items_cost += flt(d.basic_amount)

# 		return outgoing_items_cost

# def set_rate_for_outgoing_items_override(doc, method):   
#     StockEntry.set_rate_for_outgoing_items = set_rate_for_outgoing_items

class CustomStockEntry(StockEntry):
    def on_submit(self):
        self.update_stock_ledger()

        update_serial_nos_after_submit(self, "items")
        self.update_work_order()
        self.validate_subcontract_order()
        self.update_subcontract_order_supplied_items()
        self.update_subcontracting_order_status()
        self.update_pick_list_status()
        if not self.purpose == "Repack":
            self.make_gl_entries()

        self.repost_future_sle_and_gle()
        self.update_cost_in_project()
        self.validate_reserved_serial_no_consumption()
        self.update_transferred_qty()
        self.update_quality_inspection()

        if self.work_order and self.purpose == "Manufacture":
            self.update_so_in_serial_number()

        if self.purpose == "Material Transfer" and self.add_to_transit:
            self.set_material_request_transfer_status("In Transit")
        if self.purpose == "Material Transfer" and self.outgoing_stock_entry:
            self.set_material_request_transfer_status("Completed")

    def set_basic_rate(self, reset_outgoing_rate=True, raise_error_if_no_rate=True):
        """
        Set rate for outgoing, scrapped and finished items
        """
        # Set rate for outgoing items
        outgoing_items_cost = self.set_rate_for_outgoing_items(
            reset_outgoing_rate, raise_error_if_no_rate
        )
        finished_item_qty = sum(d.transfer_qty for d in self.items if d.is_finished_item)

        items = []
        # Set basic rate for incoming items
        for d in self.get("items"):
            if d.s_warehouse or d.set_basic_rate_manually:
                continue

            if d.allow_zero_valuation_rate:
                d.basic_rate = 0.0
                items.append(d.item_code)

            elif d.is_finished_item:
                if self.purpose == "Manufacture":
                    d.basic_rate = self.get_basic_rate_for_manufactured_item(
                        finished_item_qty, outgoing_items_cost
                    )
                elif self.purpose == "Repack":
                    d.basic_rate = self.get_basic_rate_for_repacked_items(d.transfer_qty, outgoing_items_cost)

            if not d.basic_rate and not d.allow_zero_valuation_rate:
                d.basic_rate = get_valuation_rate(
                    d.item_code,
                    d.t_warehouse,
                    self.doctype,
                    self.name,
                    d.allow_zero_valuation_rate,
                    currency=erpnext.get_company_currency(self.company),
                    company=self.company,
                    raise_error_if_no_rate=raise_error_if_no_rate,
                    batch_no=d.batch_no,
                )

            # do not round off basic rate to avoid precision loss
            d.basic_rate = flt(d.basic_rate)
            d.basic_amount = flt(flt(d.transfer_qty) * flt(d.basic_rate), d.precision("basic_amount"))

        if items:
            message = ""

            if len(items) > 1:
                message = _(
                    "Items rate has been updated to zero as Allow Zero Valuation Rate is checked for the following items: {0}"
                ).format(", ".join(frappe.bold(item) for item in items))
            else:
                message = _(
                    "Item rate has been updated to zero as Allow Zero Valuation Rate is checked for item {0}"
                ).format(frappe.bold(items[0]))

            frappe.msgprint(message, alert=True)

    def set_rate_for_outgoing_items(self, reset_outgoing_rate=True, raise_error_if_no_rate=True):
        outgoing_items_cost = 0.0
        for d in self.get("items"):
            if d.s_warehouse:
                if reset_outgoing_rate:
                    args = self.get_args_for_incoming_rate(d)
                    rate = get_incoming_rate(args, raise_error_if_no_rate)
                    if rate > 0:
                        d.basic_rate = rate

                d.basic_amount = flt(flt(d.transfer_qty) * flt(d.basic_rate), d.precision("basic_amount"))
                if not d.t_warehouse:
                    outgoing_items_cost += flt(d.basic_amount)

        return outgoing_items_cost    
