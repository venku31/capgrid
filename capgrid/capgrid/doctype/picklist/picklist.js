// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on("PickList Details", {
  qty: function (frm, cdt, cdn) {
    total_qty(frm, cdt, cdn);
  },
  picked_qty: function (frm, cdt, cdn) {
    total_qty(frm, cdt, cdn);
  },
  validate: function (frm, cdt, cdn) {
    total_qty(frm, cdt, cdn);
    fetch_sales_order_rate_tax(frm, cdt, cdn);
    // cur_frm.save();
  },

});
frappe.ui.form.on("PickList", {
  validate: function (frm, cdt, cdn) {
    total_qty(frm, cdt, cdn);
    fetch_actual_qty(frm, cdt, cdn);
    fetch_sales_order_rate_tax(frm, cdt, cdn);
   
  },
  sales_order: function (frm, cdt, cdn) {
    cur_frm.refresh_fields()
		cur_frm.save()
  },
});

// frappe.ui.form.on("PickList", "validate", function(frm, cdt, cdn) {
// 	$.each(frm.doc.details || [], function(i, d) {
// 		if(d.part_number){
// 		console.log("first call")
// 		frappe.call({
// 				method: "capgrid.capgrid.doctype.pick_list_upload.pick_list_upload.get_actual_stock",
// 				args: {"warehouse":frm.doc.warehouse,"part_number":d.part_number},
// 				callback: function(r) {
// 					console.log(r.message);
// 					var price = r.message[0].actual_qty
// 					frappe.model.set_value(cdt, cdn, d.actual_stock, price);
// 		d.actual_stock=price
// 				}
// 			});
// 		}
// 	   })
// 	  refresh_field("details");
// 	})

function total_qty(frm, cdt, cdn) {
  // estimated_amount: function(frm, cdt, cdn) {
  var d = locals[cdt][cdn];
  var total_qty = 0;
  var total_picked_qty = 0;
  frm.doc.details.forEach(function (d) {
    total_qty += d.qty;
  });
  frm.doc.details.forEach(function (d) {
    total_picked_qty += d.picked_qty;
  });
  frm.set_value("total_qty", total_qty);
  frm.set_value("total_picked_qty", total_picked_qty);
  cur_frm.set_value("created_by", frappe.session.user);
}

function fetch_actual_qty(frm, cdt, cdn) {
  $.each(frm.doc.details || [], function (i, d) {
    if (d.part_number) {
      frappe.call({
        method: "capgrid.capgrid.doctype.picklist.picklist.get_actual_stock",
        args: { warehouse: frm.doc.warehouse, part_number: d.part_number },
        callback: function (r) {
          console.log(r.message);
          var actual_qty = r.message.actual_qty;
          frappe.model.set_value(cdt, cdn, d.actual_stock, actual_qty);
          d.actual_stock = actual_qty;
        },
      });
    }
  });
}

function fetch_sales_order_rate_tax(frm, cdt, cdn) {
  $.each(frm.doc.details || [], function (i, d) {
    if (frm.doc.sales_order) {
      frappe.call({
        method: "capgrid.capgrid.doctype.picklist.picklist.sales_order_price",
        args: { sales_order: frm.doc.sales_order, part_number: d.part_number },
        callback: function (r) {
          console.log(r.message);
          var rate = r.message[0].rate;
          var tax_template = r.message[0].item_tax_template
          frappe.model.set_value(cdt, cdn, d.price, rate);
          frappe.model.set_value(cdt, cdn, d.item_tax_template, tax_template);
          d.price = rate;
          d.item_tax_template = tax_template
        },
      });
    }
  });
}
frappe.ui.form.on("PickList", {
  refresh: function(frm, cdt, cdn) {
    if (frm.doc.sales_order) {
      frappe.call({
        method: "capgrid.capgrid.doctype.picklist.picklist.sales_order_price",
        args: { sales_order: frm.doc.sales_order, part_number: d.part_number },
        callback: function (r) {
          console.log(r.message);
          var rate = r.message[0].rate;
          var tax_template = r.message[0].item_tax_template
          frm.doc.details.forEach(function(d) { d.price = rate; });
      frm.doc.details.forEach(function(d) { d.item_tax_template= tax_template; });
        },
      });
    }
    cur_frm.refresh_fields()
  },
})