// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quality Inspection Page', {
	scan_barcode: function(frm, cdt, cdn){
		fetch_batch_entry(frm, cdt, cdn);	
	}
});
function fetch_batch_entry(frm, cdt, cdn) {
	console.log("1")
	frappe.call({
	  "method": "capgrid.capgrid.doctype.quality_inspection_page.quality_inspection_page.search_batch",
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
		  frappe.model.set_value(child.doctype, child.name, "packet", stock.packet)
		  frappe.model.set_value(child.doctype, child.name, "purchase_receipt", stock.purchase_receipt)
		  frappe.model.set_value(child.doctype, child.name, "inward_grn", stock.grn)
		  });
	    cur_frm.refresh_fields()
			
	  }
	  
	});
	cur_frm.fields_dict.my_field.$input.on("click", function(evt){

	})
};
