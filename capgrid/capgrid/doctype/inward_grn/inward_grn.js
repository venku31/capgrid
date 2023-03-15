// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Inward GRN', {
// 	// refresh: function(frm) {

// 	// }
// });
// frappe.ui.form.on('Inward GRN', {
// 	validate(frm) {
//     var a = frappe.model.add_child(cur_frm.doc, "Inward GRN", "inward_grn_item_details");
//     a.part_number = b.part_number;
//     a.packet = b.packet;
//     // refresh_field("inward_grn_item");

//  }
// })
frappe.ui.form.on("Inward GRN", {
   button: function(frm){
   frm.doc.inward_grn_item.forEach(function(item){ //Target Table
   var a = frappe.model.add_child(cur_frm.doc, "Inward GRN", "inward_grn_item_details");
    	a.part_number = item.part_number;
		a.qty = item.qty;
		a.packet = item.packet; //Source table field copied to Target field
    // }
    refresh_field("inward_grn_item_details");
       });
       }
    });