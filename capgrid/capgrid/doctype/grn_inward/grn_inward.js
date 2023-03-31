// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

// frappe.ui.form.on('GRN Inward', {
// 	// refresh: function(frm) {

// 	// }
// });
frappe.ui.form.on("GRN Inward", {
	on_submit: function(frm, cdt, cdn) {
      // frm.disable_save();
      // cur_frm.page.clear_actions_menu()
		
   //    frm.add_custom_button(__("Update"),function () {
   //       frm.save();
   //   }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
   if (!frm.doc.purchase_receipt){
      // cur_frm.page.clear_actions_menu()
		// frm.disable_save();
      // frm.add_custom_button(__("Generate GRN"),function () {
         frappe.call({
            method: 'capgrid.capgrid.doctype.grn_inward.grn_inward.create_pr',
            args: {
               'company':frm.doc.company,
               'supplier': frm.doc.supplier,
               'product_description' : frm.doc.grn_inward_item,
               'bill_no' : frm.doc.supplier_invoice_no,
               'bill_date' : frm.doc.supplier_invoice_date,
               // 'purchase_receipt' : frm.doc.purchase_receipt
            },
            callback(r) {
               if (r.message){
                  console.log(r.message)
                  // cur_frm.set_value("purchase_receipt", r.message);
            
               }
               frappe.db.set_value("GRN Inward",cur_frm.doc.name,"purchase_receipt", r.message);
            }
         })  
         refresh_field("grn_inward");
         // frm.save()
   //   }).css({'color':'white','font-weight': 'bold', 'background-color': 'Green'});
   }
   var me = this;
   var doc = frm.doc
   var print_format = "BarcodePacketLabel"; // print format name
   
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
});
// frappe.ui.form.on("Inward GRN", {
//    validate: function(frm){ 
//       cur_frm.clear_table("inward_grn_item_details");
//       frm.doc.inward_grn_item.forEach(function(item){ 
//          var total_qty = 0;
//          total_qty +=  ((item.qty/item.packet));
//          for (let i = 0; i < item.packet; i++) {
//       var a = frappe.model.add_child(cur_frm.doc, "Inward GRN", "inward_grn_item_details");
//       a.part_number = item.part_number;
//       a.item_name = item.description;
//       a.purchase_order = frm.doc.purchase_order;
//       a.type_of_po = frm.doc.po_type;
// 		a.qty = item.qty/item.packet;
// 		a.packet = i+1; 
//     // }
//    }
//      refresh_field("inward_grn_item_details");
//        });
//        }
//     });

frappe.ui.form.on("GRN Inward Item", {
   update: function(frm, cdt, cdn){ 
      var item = locals[cdt][cdn];
      cur_frm.clear_table("grn_inward_item_details");
      frm.doc.grn_inward_item.forEach(function(item){ 
         var total_qty = 0;
         total_qty +=  ((item.qty/item.packet));
         for (let i = 0; i < item.packet; i++) {
      var a = frappe.model.add_child(cur_frm.doc, "GRN Inward", "grn_inward_item_details");
      a.part_number = item.part_number;
      a.item_name = item.description;
      // a.purchase_order = frm.doc.purchase_order || "";
      a.type_of_po = frm.doc.po_type;
		a.qty = item.qty/item.packet;
      a.lot_no = item.lot_no;
		a.packet = i+1; 
    // }
   }
     refresh_field("grn_inward_item_details");
       });
       frm.save();
       },
   // validate: function(frm, cdt, cdn){ 
   //       var item = locals[cdt][cdn];
   //       cur_frm.clear_table("grn_inward_item_details");
   //       frm.doc.grn_inward_item.forEach(function(item){ 
   //          var total_qty = 0;
   //          total_qty +=  ((item.qty/item.packet));
   //          for (let i = 0; i < item.packet; i++) {
   //       var a = frappe.model.add_child(cur_frm.doc, "GRN Inward", "grn_inward_item_details");
   //       a.part_number = item.part_number;
   //       a.item_name = item.description;
   //       a.purchase_order = frm.doc.purchase_order;
   //       a.type_of_po = frm.doc.po_type;
   //       a.qty = item.qty/item.packet;
   //       a.lot_no = item.lot_no;
   //       a.packet = i+1; 
   //     // }
   //    }
   //    //   refresh_field("grn_inward_item_details");
   //        });
   //       //  frm.save();
   //        }  
    });

    frappe.ui.form.on('GRN Inward', {
      generate_grn(frm) {
      frappe.call({
                  method: 'capgrid.capgrid.doctype.grn_inward.grn_inward.create_pr',
                  args: {
                     'company':frm.doc.company,
                     'supplier': frm.doc.supplier,
                     'product_description' : frm.doc.inward_grn_item_details,
                     'bill_no' : frm.doc.supplier_invoice_no,
                     'bill_date' : frm.doc.supplier_invoice_date,
                     // 'purchase_receipt' : frm.doc.purchase_receipt
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

   frappe.ui.form.on('GRN Inward', {
      on_submit: function(frm, cdt, cdn) {
      
      var me = this;
      var doc = frm.doc
      var print_format = "BarcodePacketLabel"; // print format name
      
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
      },
      generate_barcode: function(frm, cdt, cdn) {
      
      var me = this;
      var doc = frm.doc
      var print_format = "BarcodePacketLabel"; // print format name
      
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

	cur_frm.fields_dict.purchase_order.get_query = function(doc) {
		return {
			filters: {
				supplier:cur_frm.doc.supplier
			}
		}
	}
   
   this.frm.cscript.onload = function(frm) {
      this.frm.set_query("part_number","grn_inward_item", function() {
        return {
                query: "capgrid.capgrid.doctype.grn_inward.grn_inward.po_item_query",
                filters: {'parent': cur_frm.doc.purchase_order}
        }
      });
   }

   frappe.ui.form.on('GRN Inward Item', {
      print_barcode: function(frm, cdt, cdn) {
      var me = this;
      var doc = frm.doc
      var print_format = "BarcodePacketLabel"; // print format name
      
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
  