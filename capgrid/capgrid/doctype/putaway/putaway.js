// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Putaway', {
	scan_barcode: function(frm){
		fetch_batch_entry(frm);	
	},
	// update: (frm) => {
	// 	if (frm.doc.update_location){
	// 		frappe.call({
	// 			method: 'capgrid.capgrid.doctype.putaway.putaway.update_part_number_location',
	// 			args: {
	// 			   'item_code' : frm.doc.part_number,
	// 			   'company' : frm.doc.company,
	// 			   'update_location':frm.doc.update_location,
	// 			   'location':frm.doc.location,
	// 			//    'warehouse': frappe.db.get_value("Warehouse Location", filters={"name": frm.doc.update_location}, fieldname="warehouse"),
	// 			},
	// 			callback(r) {
	// 			   if (r.message){
	// 				  console.log(r.message)
				
	// 			   }
	// 			}
	// 		 })  
	// 		}
	// 	},
		refresh: function(frm) {
			cur_frm.fields_dict.main_warehouse.get_query = function(doc) {
				return {
				   filters: {
					  company:frm.doc.company,
					  is_group:1
				   }
				}
				},
			cur_frm.fields_dict.scan_location.get_query = function(doc) {
			 return {
				filters: {
				   company:frm.doc.company,
				   main_warehouse:frm.doc.main_warehouse
				//    warehouse:frm.doc.warehouse
				}
			 }
			}}	
});
function fetch_batch_entry(frm) {
	console.log("1")
	frappe.call({
	  "method": "capgrid.capgrid.doctype.putaway.putaway.search_lot",
	  "args": {
		"batch": frm.doc.scan_barcode,
		"company":frm.doc.company,
		// "main_warehouse":frm.doc.main_warehouse,
	   },
	  callback: function (r) {
		console.log(r)
		// cur_frm.clear_table("details");
		r.message.forEach(stock => {
		//   var child = cur_frm.add_child("putaway_details");
		//   cur_frm.set_value("scan_barcode","")
		//   frappe.model.set_value(child.doctype, child.name, "part_number", stock.part_number)
		//   frappe.model.set_value(child.doctype, child.name, "batch_no", stock.batch_no)
		//   frappe.model.set_value(child.doctype, child.name, "description", stock.description)
		//   frappe.model.set_value(child.doctype, child.name, "location", stock.location)
		// //   frappe.model.set_value(child.doctype, child.name, "purchase_receipt", stock.purchase_receipt)
		// //   frappe.model.set_value(child.doctype, child.name, "inward_grn", stock.grn)
		//   frappe.model.set_value(child.doctype, child.name, "lot_no", stock.lot_no)
		  cur_frm.set_value("part_number", stock.part_number)
		  cur_frm.set_value("lot_no", stock.lot_no)
		  cur_frm.set_value("batch_no", stock.batch_no)
		  cur_frm.set_value("description", stock.description)
		  cur_frm.set_value("location", stock.location)
		  cur_frm.set_value("lot_status", stock.status)
		  cur_frm.set_value("main_warehouse", stock.main_warehouse)
		//   cur_frm.set_value("grn", stock.grn)
		//   cur_frm.set_value("purchase_order", stock.purchase_order)
		//   cur_frm.set_value("purchase_receipt", stock.purchase_receipt)
		//   cur_frm.set_value("created_by", stock.owner)
		  });
	    cur_frm.refresh_fields()
			
	  }
	  
	});
	cur_frm.fields_dict.my_field.$input.on("click", function(evt){

	})
};
frappe.ui.form.on('Putaway', {
	validate(frm) {
		if (frm.doc.location){
			if ((frm.doc.scaned_location != frm.doc.location) &&(!cur_frm.doc.override)){
			  frappe.msgprint(__("Wrong Part Number Location, Enable Override to move lot number to temporary location"));
			  frappe.validated = false;
		  	}
			  	
		}
		cur_frm.doc.scaned_location = cur_frm.doc.scan_location
			cur_frm.refresh_fields()
	},

	scan_location(frm) {
		cur_frm.doc.scaned_location = cur_frm.doc.scan_location
		cur_frm.refresh_fields()
		cur_frm.save()
	},
	override(frm) {
		cur_frm.refresh_fields()
		cur_frm.save()
	},
	onload_post_render: function(frm) {
			frm.get_field("create_new").$input.addClass('btn-primary');
			},
			on_submit: function(frm, cdt, cdn) {
				frappe.set_route("Form", "Putaway", "new_putaway");
			},
	before_cancel: function(frm) {
			frappe.msgprint(__("Please Cance Stock Entry"));
			frappe.validated = false;
				
         },
})

// frappe.ui.form.on('Putaway Details', {
// 	batch_no: function(frm, cdt, cdn) {
// 		var d = locals[cdt][cdn];
// 		$.each(frm.doc.putaway_details, function(i, row) {
// 			if (row.batch_no === d.batch_no && row.name != d.name) {
// 			   frappe.msgprint('Lot No already exists on the table.');
// 			   frappe.model.remove_from_locals(cdt, cdn);
// 			   frm.refresh_field('putaway_details');
// 			   return false;
// 			}
// 		});
// 	},
// 	actual_location: function(frm, cdt, cdn) {
// 		var d = locals[cdt][cdn];
// 		$.each(frm.doc.putaway_details, function(i, row) {
// 			if (row.actual_location === d.location) {
// 			   frappe.msgprint('Lot No already exists on the table.');
// 			//    frappe.model.remove_from_locals(cdt, cdn);
// 			   frm.refresh_field('putaway_details');
// 			   return false;
// 			}
// 		});
// 	}
// });
