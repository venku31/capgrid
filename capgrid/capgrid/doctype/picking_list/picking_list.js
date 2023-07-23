// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Picking List', {
	refresh: function(frm) {
		if(frm.doc.company && frm.doc.warehouse){
			frappe.call({
				method: "capgrid.capgrid.doctype.picking_list.picking_list.get_stock_warehouse_locations",
				args: {warehouse: frm.doc.warehouse, company: frm.doc.company,item_code:frm.doc.part_number}
			}).then(resp => {
				if(resp.message){
					let html_data = `<table class="table table-bordered small " style="margin-bottom:10px;">
					<thead>
						<tr>
							<th style="width: 8%" class="text-right">Location</th>
							<th style="width: 8%" class="text-right">Balance Qty</th>
						</tr>
					</thead>
					<tbody>`
					// resp.message.map(item => {
					// 	html_data += `<tr> <td> ${item.item_code} </td>
					// 	<td class="text-right"> ${item.warehouse} </td>
					// 	<td class="text-right"> ${item.warehouse_location} </td>
					// 	<td class="text-right"> ${item.lot_number} </td>
					// 	<td class="text-right"> ${item.actual_qty} </td>
					// </tr>`
					resp.message.map((item,idx) => {
						html_data += 
						`<tr> 
						<td class="text-right"> ${item.warehouse_location} </td>
						<td class="text-right"> ${item.actual_qty} </td>
					</tr>`
					// html_data += `</tbody></table>`
					})
					frm.get_field("stock_details").$wrapper.html(html_data);
					// frm.get_field('stock_details').html(html_data)
					
				}
			})
		}
		fetch_part_number_qty(frm);	
		
	},
	scan_location(frm) {
		cur_frm.doc.warehouse_location = cur_frm.doc.scan_location
		cur_frm.refresh_fields()
	},
	scan_barcode: function(frm){
		fetch_lot_entry(frm);	
		// cur_frm.refresh_fields()
		// cur_frm.save()
	},
	// before_save: function(frm){
	// 	fetch_part_number_qty(frm);	
	// 	cur_frm.refresh_fields()
	// },
	part_number: function(frm){
		
		if(frm.doc.company && frm.doc.warehouse){
			frappe.call({
				method: "capgrid.capgrid.doctype.picking_list.picking_list.get_stock_warehouse_locations",
				args: {warehouse: frm.doc.warehouse, company: frm.doc.company,item_code:frm.doc.part_number}
			}).then(resp => {
				if(resp.message){
					let html_data = `<table class="table table-bordered small " style="margin-bottom:10px;">
					<thead>
						<tr>
							<th style="width: 8%" class="text-right">Location</th>
							<th style="width: 8%" class="text-right">Balance Qty</th>
						</tr>
					</thead>
					<tbody>`
					// resp.message.map(item => {
					// 	html_data += `<tr> <td> ${item.item_code} </td>
					// 	<td class="text-right"> ${item.warehouse} </td>
					// 	<td class="text-right"> ${item.warehouse_location} </td>
					// 	<td class="text-right"> ${item.lot_number} </td>
					// 	<td class="text-right"> ${item.actual_qty} </td>
					// </tr>`
					resp.message.map((item,idx) => {
						html_data += 
						`<tr> 
						<td class="text-right"> ${item.warehouse_location} </td>
						<td class="text-right"> ${item.actual_qty} </td>
					</tr>`
					// html_data += `</tbody></table>`
					})
					frm.get_field("stock_details").$wrapper.html(html_data);
					// frm.get_field('stock_details').html(html_data)
					
				}
			})
		}
		fetch_part_number_qty(frm);	
	},
	validate: function(frm){
		if(frm.doc.workflow_state ="Pending" && frm.doc.total_scaned_qty){
			frm.doc.workflow_state ="Picking Started"
		}
	}
// 	this.frm.cscript.onload = function(frm) {
// 		this.frm.set_query("part_number","grn_inward_item", function() {
// 		  return {
// 				  query: "capgrid.capgrid.doctype.grn_inward.grn_inward.po_item_query",
// 				  filters: {'parent': cur_frm.doc.purchase_order}
// 		  }
// 		});
// 	 }
// validate: function(frm, cdt, cdn) {
// 	if (frm.doc.total_scaned_qty>0 && frm.doc.total_scaned_qty>frm.doc.to_be_picked){
// 		  frappe.msgprint(__("Total Inward Qty Greater than PO Qty"));
// 		  frappe.validated = false;
// 	   }
	   
// 	},
});
frappe.ui.form.on('Picking List Item Details', {
	qty: function(frm, cdt, cdn) {
		total_scaned_qty(frm, cdt, cdn)
		frm.save();
		},
	part_details_remove: function (frm, cdt, cdn) {
		total_scaned_qty(frm, cdt, cdn);
		frm.save();
		  },  
	lot_number: function(frm, cdt, cdn) {
			var d = locals[cdt][cdn];
			$.each(frm.doc.part_details, function(i, row) {
				if (row.lot_number === d.lot_number && row.name != d.name) {
				   frappe.msgprint('Lot No already exists on the table.');
				   frappe.model.remove_from_locals(cdt, cdn);
				   frm.refresh_field('part_details');
				   return false;
				}
			});
		},
	})

function fetch_lot_entry(frm) {
	console.log("1")
	frappe.call({
	  "method": "capgrid.capgrid.doctype.picking_list.picking_list.scan_lot",
	  "args": {
		"lot_no": frm.doc.scan_barcode,
		"company":frm.doc.company,
		"warehouse_location":frm.doc.warehouse_location,
	   },
	  callback: function (r) {
		console.log(r)
		// cur_frm.clear_table("details");
		r.message.forEach(stock => {
			var child = cur_frm.add_child("part_details");
			cur_frm.set_value("scan_barcode","")
			frappe.model.set_value(child.doctype, child.name, "part_number", stock.item_code)
			frappe.model.set_value(child.doctype, child.name, "qty", stock.actual_qty)
			frappe.model.set_value(child.doctype, child.name, "lot_number", stock.lot_number)
			frappe.model.set_value(child.doctype, child.name, "qty", stock.actual_qty)
			frappe.model.set_value(child.doctype, child.name, "warehouse_location", stock.warehouse_location)
			frappe.model.set_value(child.doctype, child.name, "uom", stock.stock_uom)
		   });
	    // cur_frm.refresh_fields()
			
	  }
	  
	});
	// cur_frm.fields_dict.my_field.$input.on("click", function(evt){

	// })
};

function total_scaned_qty(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var total_scaned_qty = 0;
    frm.doc.part_details.forEach(function(d) { total_scaned_qty += d.qty});
    frm.set_value('total_scaned_qty', total_scaned_qty);
    }	

	this.frm.cscript.onload = function(frm) {
		this.frm.set_query("part_number", function() {
			return {
					  query: "capgrid.capgrid.doctype.picking_list.picking_list.picklist_item_query",
				 filters: {parent:cur_frm.doc.picklist}
			}
		});
	}

	function fetch_part_number_qty(frm) {
		console.log("1")
		frappe.call({
		  "method": "capgrid.capgrid.doctype.picking_list.picking_list.picklist_item_qty",
		  "args": {
			"picklist": frm.doc.picklist,
			"part_number":frm.doc.part_number,
		   },
		  callback: function (r) {
			console.log(r)
			// cur_frm.clear_table("details");
			r.message.forEach(stock => {
				// var child = cur_frm.add_child("part_details");
				cur_frm.set_value("to_be_picked",stock.to_be_picked)
				
			   });
			cur_frm.refresh_fields()
				
		  }
		  
		});
		cur_frm.fields_dict.my_field.$input.on("click", function(evt){
	
		})
	};
	