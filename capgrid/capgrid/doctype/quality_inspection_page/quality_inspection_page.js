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
	save: function(frm, cdt, cdn){
	frappe.call({
		method: 'capgrid.capgrid.doctype.quality_inspection_page.quality_inspection_page.create_status_stock_entry',
		args: {
		   'company' : frm.doc.company,
		   'main_warehouse' : frm.doc.main_warehouse,
		   'purchase_order' : frm.doc.purchase_order,
		   'purchase_receipt' : frm.doc.purchase_receipt,
		   'product_description' : frm.doc.quality_inspection_page_table,
		},
		callback(r) {
		   if (r.message){
			  console.log(r.message)
		
		   }
		}
	 }) 
	}

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
		  cur_frm.set_value("company", stock.company)
		  cur_frm.set_value("main_warehouse", stock.main_warehouse)
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
				if(cur_frm.doc.status=="Rejected") {
					d.rejected_qty=d.qty;
				   d.hold_qty=0;
				   d.accepted_qty=d.qty-d.rejected_qty-d.hold_qty;
				   }
				   else if(cur_frm.doc.status=="Accepted") {
					d.rejected_qty=0;
				   d.hold_qty=0;
				   d.accepted_qty=d.qty-d.rejected_qty-d.hold_qty;
				   }
				   else if(cur_frm.doc.status=="On Hold") {
					d.rejected_qty=0;
				   d.hold_qty=d.qty;
				   d.accepted_qty=d.qty-d.rejected_qty-d.hold_qty;
				   }
				   else {
				   d.accepted_qty=d.qty;
				   d.rejected_qty=0;
				   d.hold_qty=0;
				   }
				});
				cur_frm.refresh_fields()
		},
		onload_post_render: function(frm) {
			frm.get_field("create_new").$input.addClass('btn-primary');
			},
			on_submit: function(frm, cdt, cdn) {
				frappe.set_route("Form", "Quality Inspection Page", "new_quality_inspection_page");
			},
			before_cancel: function(frm) {
				frappe.msgprint(__("Please Cance Stock Entry"));
				frappe.validated = false;
				
         },
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
		},
		status: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		$.each(frm.doc.quality_inspection_page_table || [], function(i, d) {
		if(d.status=="Rejected") {
	 	d.rejected_qty=d.qty;
		d.hold_qty=0;
		d.accepted_qty=d.qty-d.rejected_qty-d.hold_qty;
		}
		else if(d.status=="Accepted") {
	 	d.rejected_qty=0;
		d.hold_qty=0;
		d.accepted_qty=d.qty-d.rejected_qty-d.hold_qty;
		}
		else if(d.status=="On Hold") {
	 	d.rejected_qty=0;
		d.hold_qty=d.qty;
		d.accepted_qty=d.qty-d.rejected_qty-d.hold_qty;
		}
		else {
		d.accepted_qty=d.qty;
		d.rejected_qty=0;
		d.hold_qty=0;
		}
		});
		qi_total_qty(frm, cdt, cdn);
		refresh_field("quality_inspection_page_table");
		},
		// update: function(frm, cdt, cdn)  {
		// 	var d = locals[cdt][cdn];
		// 	if (d.current_status){
		// 		frappe.call({
		// 			method: 'capgrid.capgrid.doctype.quality_inspection_page.quality_inspection_page.create_status_stock_entry',
		// 			args: {
		// 			   'company' : frm.doc.company,
		// 			   'main_warehouse' : frm.doc.main_warehouse,
		// 			   'purchase_order' : frm.doc.purchase_order,
		// 			   'purchase_receipt' : frm.doc.purchase_receipt,
		// 			   'product_description' : frm.doc.quality_inspection_page_table,
		// 			},
		// 			callback(r) {
		// 			   if (r.message){
		// 				  console.log(r.message)
					
		// 			   }
		// 			}
		// 		 })  
		// 		}
		// 	},
		});

function qi_total_qty(frm, cdt, cdn) {
    // estimated_amount: function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var total_inward_qty = 0;
    var total_accepted_qty = 0;
	var total_rejected_qty = 0;
	var total_hold_qty = 0;
    frm.doc.quality_inspection_page_table.forEach(function(d) { total_inward_qty += d.qty});
    frm.doc.quality_inspection_page_table.forEach(function(d) { total_accepted_qty += d.accepted_qty});
	frm.doc.quality_inspection_page_table.forEach(function(d) { total_rejected_qty += d.rejected_qty});
	frm.doc.quality_inspection_page_table.forEach(function(d) { total_hold_qty += d.hold_qty});
    frm.set_value('total_inward_qty', total_inward_qty);
    frm.set_value('total_accepted_qty', total_accepted_qty);
	frm.set_value('total_rejected_qty', total_rejected_qty);
	frm.set_value('total_hold_qty', total_hold_qty);
      }	