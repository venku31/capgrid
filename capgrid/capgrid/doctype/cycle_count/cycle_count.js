// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cycle Count', {
	// refresh: function(frm) {

	// }
	lot_no_scan: function(frm){
		fetch_lot_entry(frm);	

	},
	onload_post_render: function(frm) {
		frm.get_field("next_part").$input.addClass('btn-primary');
		},
	next_part: function(frm){
	frappe.set_route("Form", "Cycle Count", "new-cycle-count-1");
	}
});

function fetch_lot_entry(frm) {
	console.log("1")
	frappe.call({
	  "method": "capgrid.capgrid.doctype.cycle_count.cycle_count.scan_lot",
	  "args": {
		"lot_no": frm.doc.lot_no_scan,
		"warehouse_location":frm.doc.location,
	   },
	  callback: function (r) {
		console.log(r)
		// cur_frm.clear_table("details");
		r.message.forEach(stock => {
			var child = cur_frm.add_child("cycle_count_details");
			cur_frm.set_value("lot_no_scan","")
			frappe.model.set_value(child.doctype, child.name, "item_code", stock.item_code)
			frappe.model.set_value(child.doctype, child.name, "quantity", stock.actual_qty)
			frappe.model.set_value(child.doctype, child.name, "lot_number", stock.lot_number)
			// frappe.model.set_value(child.doctype, child.name, "qty", stock.actual_qty)
			frappe.model.set_value(child.doctype, child.name, "location", stock.warehouse_location)
		   });
	    // cur_frm.refresh_fields()
			
	  }
	  
	});
	// cur_frm.fields_dict.my_field.$input.on("click", function(evt){

	// })
};

frappe.ui.form.on('Cycle Count Details', {
	quantity: function(frm, cdt, cdn) {
		total_scaned_qty(frm, cdt, cdn)
		frm.save();
		},
		cycle_count_details_remove: function (frm, cdt, cdn) {
		total_scaned_qty(frm, cdt, cdn);
		frm.save();
	},
})

function total_scaned_qty(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var total_scaned_qty = 0;
    frm.doc.cycle_count_details.forEach(function(d) { total_scaned_qty += d.quantity});
    frm.set_value('total_qty', total_scaned_qty);
    }	

	
