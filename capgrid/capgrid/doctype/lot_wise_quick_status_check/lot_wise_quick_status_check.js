// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lot wise Quick Status Check', {
	// refresh: function(frm) {

	// }
	scan_lot: function(frm){
		fetch_lot_entry(frm);	

	},
});


function fetch_lot_entry(frm) {
	console.log("1")
	frappe.call({
	  "method": "capgrid.capgrid.doctype.lot_wise_quick_status_check.lot_wise_quick_status_check.scan_lot",
	  "args": {
		"lot_no": frm.doc.scan_lot,
	   },
	  callback: function (r) {
		console.log(r)
		// cur_frm.clear_table("details");
		r.message.forEach(stock => {
			cur_frm.set_value("scan_lot","")
			cur_frm.set_value("lot_number",stock.lot_number)
			cur_frm.set_value("qty",stock.actual_qty)
			cur_frm.set_value("location",stock.warehouse_location)
		
		   });
	    // cur_frm.refresh_fields()
			
	  }
	  
	});
}
	