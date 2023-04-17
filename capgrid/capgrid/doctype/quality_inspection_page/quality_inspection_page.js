// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quality Inspection Page', {
	scan_barcode: function(frm){
		fetch_batch_entry(frm);	
	},
	validate: function(frm, cdt, cdn){
		qi_total_qty(frm, cdt, cdn);
		refresh_field("quality_inspection_page_table");	
	},
});
function fetch_batch_entry(frm) {
	console.log("1")
	frappe.call({
	  "method": "capgrid.capgrid.doctype.quality_inspection_page.quality_inspection_page.search_lot",
	  "args": {
		"batch": frm.doc.scan_barcode,
	   },
	  callback: function (r) {
		console.log(r)
		// cur_frm.clear_table("details");
		r.message.forEach(stock => {
		  var child = cur_frm.add_child("quality_inspection_page_table");
		  cur_frm.set_value("scan_barcode","")
		  frappe.model.set_value(child.doctype, child.name, "part_number", stock.part_number)
		  frappe.model.set_value(child.doctype, child.name, "batch_no", stock.batch_no)
		  frappe.model.set_value(child.doctype, child.name, "description", stock.item_name)
		  frappe.model.set_value(child.doctype, child.name, "qty", stock.qty)
		  frappe.model.set_value(child.doctype, child.name, "accepted_qty", stock.qty)
		  frappe.model.set_value(child.doctype, child.name, "packet", stock.packet)
		  frappe.model.set_value(child.doctype, child.name, "purchase_receipt", stock.purchase_receipt)
		  frappe.model.set_value(child.doctype, child.name, "inward_grn", stock.grn)
		  frappe.model.set_value(child.doctype, child.name, "lot_no", stock.lot_no)
		  cur_frm.set_value("supplier", stock.supplier)
		  cur_frm.set_value("supplier_name", stock.supplier_name)
		  cur_frm.set_value("supplier_invoice_no", stock.supplier_invoice_no)
		  cur_frm.set_value("supplier_invoice_date", stock.supplier_invoice_date)
		  cur_frm.set_value("grn", stock.grn)
		  cur_frm.set_value("purchase_order", stock.purchase_order)
		  cur_frm.set_value("purchase_receipt", stock.purchase_receipt)
		  cur_frm.set_value("created_by", stock.owner)
		  });
	    cur_frm.refresh_fields()
			
	  }
	  
	});
	cur_frm.fields_dict.my_field.$input.on("click", function(evt){

	})
};

frappe.ui.form.on('Quality Inspection Page', {
		status: function(frm, cdt, cdn){
			$.each(frm.doc.quality_inspection_page_table || [], function(i, d) {
				d.status=cur_frm.doc.status;
				});
				cur_frm.refresh_fields()
		},
		onload_post_render: function(frm) {
			frm.get_field("create_new").$input.addClass('btn-primary');
			},
			create_new: function(frm, cdt, cdn) {
				frappe.set_route("Form", "Quality Inspection Page", "new_quality_inspection_page");
			}
	});
	
frappe.ui.form.on('Quality Inspection Page Table', {
		batch_no: function(frm, cdt, cdn) {
			var d = locals[cdt][cdn];
			$.each(frm.doc.quality_inspection_page_table, function(i, row) {
				if (row.batch_no === d.batch_no && row.name != d.name) {
				   frappe.msgprint('Lot No already exists on the table.');
				   frappe.model.remove_from_locals(cdt, cdn);
				   frm.refresh_field('quality_inspection_page_table');
				   return false;
				}
			});
		},
		rejected_qty: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		$.each(frm.doc.quality_inspection_page_table || [], function(i, d) {
		if(d.rejected_qty > 0) {
	 	d.accepted_qty=d.qty-d.rejected_qty;
		}
		else {
		d.accepted_qty=d.qty;	
		}
		});
		qi_total_qty(frm, cdt, cdn);
		refresh_field("quality_inspection_page_table");
		}
		});

function qi_total_qty(frm, cdt, cdn) {
    // estimated_amount: function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var total_inward_qty = 0;
    var total_accepted_qty = 0;
	var total_rejected_qty = 0;
    frm.doc.quality_inspection_page_table.forEach(function(d) { total_inward_qty += d.qty});
    frm.doc.quality_inspection_page_table.forEach(function(d) { total_accepted_qty += d.accepted_qty});
	frm.doc.quality_inspection_page_table.forEach(function(d) { total_rejected_qty += d.rejected_qty});
    frm.set_value('total_inward_qty', total_inward_qty);
    frm.set_value('total_accepted_qty', total_accepted_qty);
	frm.set_value('total_rejected_qty', total_rejected_qty);
      }	