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
// frappe.ui.form.on("Inward GRN", {
//    button: function(frm){
//    frm.doc.inward_grn_item.forEach(function(item){ //Target Table
//    var a = frappe.model.add_child(cur_frm.doc, "Inward GRN", "inward_grn_item_details");
//     	a.part_number = item.part_number;
// 		a.qty = item.qty;
// 		a.packet = item.packet; //Source table field copied to Target field
//     // }
//     refresh_field("inward_grn_item_details");
//        });
//        }
//     });
frappe.ui.form.on("Inward GRN", {
   button: function(frm){ 
      cur_frm.clear_table("inward_grn_item_details");
      frm.doc.inward_grn_item.forEach(function(item){ 
         var total_qty = 0;
         total_qty +=  ((item.qty/item.packet));
         for (let i = 0; i < item.packet; i++) {
      var a = frappe.model.add_child(cur_frm.doc, "Inward GRN", "inward_grn_item_details");
      a.part_number = item.part_number;
      a.item_name = item.item_name;
      a.purchase_order = item.purchase_order;
      a.type_of_po = item.type_o_po;
		a.qty = item.qty/item.packet;
		a.packet = i+1; 
    // }
   }
     refresh_field("inward_grn_item_details");
       });
       }
    });

    frappe.ui.form.on('Inward GRN', {
      generate_grn(frm) {
      frappe.call({
                  method: 'capgrid.capgrid.doctype.inward_grn.inward_grn.create_pr',
                  args: {
                     'company':frm.doc.company,
                     'supplier': frm.doc.supplier,
                     'product_description' : frm.doc.inward_grn_item_details,
                     'bill_no' : frm.doc.supplier_invoice_no,
                     'bill_date' : frm.doc.supplier_invoice_date,
                  },
                  callback(r) {
                     if (r.message){
                        console.log(r.message)
                        cur_frm.set_value("purchase_receipt", r.message);
                  
                     }
                  }
               })
      }
   })    

   frappe.ui.form.on('Inward GRN', {
      print_barcode: function(frm, cdt, cdn) {
      
      var me = this;
      var doc = frm.doc
      var print_format = "Barcodeprintqty"; // print format name
      
      var w = window.open(frappe.urllib.get_full_url("/printview?"
         +"doctype="+encodeURIComponent(cdt)
         +"&name="+encodeURIComponent(cdn)
         +"&trigger_print=1"
         +"&format=" + print_format
         +"&no_letterhead=0"
         ));
      
         if(!w) {
            msgprint(__("Please enable pop-ups for printing.")); return;
         }
      }
      })