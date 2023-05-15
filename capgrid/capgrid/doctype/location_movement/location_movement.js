// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Location Movement', {
refresh: function(frm) {
			cur_frm.fields_dict.main_warehouse.get_query = function(doc) {
			 return {
				filters: {
				   company:frm.doc.company,
				   is_group:1
				}
			 }
			 },
			cur_frm.fields_dict.from_warehouse.get_query = function(doc) {
				return {
				filters: {
				company:frm.doc.company
				}
				}
				},
			cur_frm.fields_dict.to_warehouse.get_query = function(doc) {
				return {
				filters: {
					company:frm.doc.company
					}
					}
					},
			cur_frm.fields_dict.part_number_location.get_query = function(doc) {
				return {
				filters: {
					company:frm.doc.company,
					main_warehouse:frm.doc.main_warehouse,
					warehouse:frm.doc.from_warehouse
					}
					}
					},
			cur_frm.fields_dict.scan_location.get_query = function(doc) {
				return {
				filters: {
				company:frm.doc.company,
				main_warehouse:frm.doc.main_warehouse,
				warehouse:frm.doc.to_warehouse
					}
					}
					}
		  },
		  scan_barcode: function(frm){
			fetch_lot_details(frm);	
		},
	// from_warehouse: function(frm, cdt, cdn){
	// $.each(frm.doc.location_details || [], function(i, d) {
	// 	d.from_warehouse=cur_frm.doc.from_warehouse;
	// 	});
	// 	cur_frm.refresh_fields()
	// 	},
	// to_warehouse: function(frm, cdt, cdn){
	// 		$.each(frm.doc.location_details || [], function(i, d) {
	// 			d.to_warehouse=cur_frm.doc.to_warehouse;
	// 			});
	// 			cur_frm.refresh_fields()
	// 			},
	scan_location(frm) {
		cur_frm.doc.scaned_location = cur_frm.doc.scan_location
		cur_frm.refresh_fields()
	},
	validate(frm) {
		cur_frm.doc.scaned_location = cur_frm.doc.scan_location
		cur_frm.refresh_fields()
	},
});

function fetch_lot_details(frm) {
	console.log("1")
	frappe.call({
	  "method": "capgrid.capgrid.doctype.location_movement.location_movement.search_location_mv_lot",
	  "args": {
		"lot_number": frm.doc.scan_barcode,
		"company":frm.doc.company,
	   },
	  callback: function (r) {
		console.log(r)
		r.message.forEach(stock => {
		  cur_frm.set_value("part_number", stock.item_code)
		//   cur_frm.set_value("lot_no", stock.lot_no)
		  cur_frm.set_value("batch_no", stock.lot_number)
		  cur_frm.set_value("from_warehouse", stock.warehouse)
		  cur_frm.set_value("part_number_location", stock.warehouse_location)
		  cur_frm.set_value("actual_qty", stock.actual_qty)
		  });
	    cur_frm.refresh_fields()
			
	  }
	  
	});
	cur_frm.fields_dict.my_field.$input.on("click", function(evt){

	})
};