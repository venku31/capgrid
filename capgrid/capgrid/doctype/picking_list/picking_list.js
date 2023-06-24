// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Picking List', {
	refresh: function(frm) {
		if(frm.doc.company && frm.doc.warehouse){
			frappe.call({
				method: "capgrid.capgrid.doctype.picking_list.picking_list.get_stock_warehouse_locations",
				args: {warehouse: frm.doc.warehouse, company: frm.doc.company}
			}).then(resp => {
				if(resp.message){
					let html_data = `<table class="table table-bordered small " style="margin-bottom:20px;">
					<thead>
						<tr>
							<th style="width: 16%">Part Number</th>
							<th style="width: 16%" class="text-right">Warehouse</th>
							<th style="width: 16%" class="text-right">Warehouse Location</th>
							<th style="width: 16%" class="text-right">Lot Number</th>
							<th style="width: 16%" class="text-right">Actual Qty</th>
						</tr>
					</thead>
					<tbody>`
					resp.message.map(item => {
						html_data += `<tr> <td> ${item.item_code} </td>
						<td class="text-right"> ${item.warehouse} </td>
						<td class="text-right"> ${item.warehouse_location} </td>
						<td class="text-right"> ${item.lot_number} </td>
						<td class="text-right"> ${item.actual_qty} </td>
					</tr>`
					html_data += `</tbody></table>`
					})

					frm.get_field('stock_details').html(html_data)
				}
			})
		}
	}
});
