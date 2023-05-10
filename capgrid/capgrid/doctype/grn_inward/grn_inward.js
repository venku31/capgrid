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
   // if (!frm.doc.purchase_receipt){
   //    // cur_frm.page.clear_actions_menu()
	// 	// frm.disable_save();
   //    // frm.add_custom_button(__("Generate GRN"),function () {
   //       frappe.call({
   //          method: 'capgrid.capgrid.doctype.grn_inward.grn_inward.create_pr',
   //          args: {
   //             'company':frm.doc.company,
   //             'supplier': frm.doc.supplier,
   //             'product_description' : frm.doc.grn_inward_item,
   //             'bill_no' : frm.doc.supplier_invoice_no,
   //             'bill_date' : frm.doc.supplier_invoice_date,
   //             'grn_inward' : frm.doc.name,
   //             'main_warehouse':frm.doc.main_warehouse,
   //             'purchase_order':frm.doc.purchase_order
   //          },
   //          callback(r) {
   //             if (r.message){
   //                console.log(r.message)
   //                cur_frm.set_value("purchase_receipt", r.message);
            
   //             }
   //             // frappe.db.set_value("GRN Inward",cur_frm.doc.name,"purchase_receipt", r.message);
   //          }
   //       })  
   //       // frm.reload_doc();
   //       refresh_field("grn_inward");
   //       // frm.save('Submit');
   // //   }).css({'color':'white','font-weight': 'bold', 'background-color': 'Green'});
   // }
   
   var me = this;
   var doc = frm.doc
   var print_format = "BarcodeLabesidebyside"; // print format name
   
   var w = window.open(frappe.urllib.get_full_url("/printview?"
      +"doctype="+encodeURIComponent(cdt)
      +"&name="+encodeURIComponent(cdn)
      +"&trigger_print=1"
      +"&format=" + print_format
      +"&no_letterhead=0"
      ));
      // if(!w) {
      //    msgprint(__("Please enable pop-ups for printing.")); return;
      // }
	},
// after_submit: function(frm, cdt, cdn) {
//   var me = this;
//    var doc = frm.doc
//    var print_format = "BarcodeLabesidebyside"; // print format name
   
//    var w = window.open(frappe.urllib.get_full_url("/printview?"
//       +"doctype="+encodeURIComponent(cdt)
//       +"&name="+encodeURIComponent(cdn)
//       +"&trigger_print=1"
//       +"&format=" + print_format
//       +"&no_letterhead=0"
//       ));
//    } 
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
frappe.ui.form.on('GRN Inward Item', {
      packet:function(frm, cdt, cdn){ 
         frm.save();   
          },
      // on_update:function(frm, cdt, cdn){ 
      //       var item = locals[cdt][cdn];
      //       cur_frm.clear_table("grn_inward_item_details");
      //       frm.doc.grn_inward_item.forEach(function(item){ 
      //          var total_qty = 0;
      //          total_qty +=  ((item.qty/item.packet));
      //          for (let i = 0; i < item.packet; i++) {
      //       var a = frappe.model.add_child(cur_frm.doc, "GRN Inward", "grn_inward_item_details");
      //       a.part_number = item.part_number;
      //       a.item_name = item.description;
      //       // a.purchase_order = frm.doc.purchase_order || "";
      //       a.type_of_po = frm.doc.po_type;
      //       a.qty = item.qty/item.packet;
      //       a.lot_no = item.lot_no;
      //       a.packet = i+1; 
      //     // }
      //    }
      //    //   refresh_field("grn_inward_item_details");
      //        });
      //       frm.save();   
      //        },
          });
frappe.ui.form.on("GRN Inward Item", {
   packet: function(frm, cdt, cdn){ 
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
   //   refresh_field("grn_inward_item_details");
       });
      //  frm.save();
       }
       });

   

   frappe.ui.form.on('GRN Inward', {
   //    refresh: function(frm, cdt, cdn) {
   //    frm.add_custom_button(__("Update Lot"),function () {
   //    var item = locals[cdt][cdn];
   //    cur_frm.clear_table("grn_inward_item_details");
   //    frm.doc.grn_inward_item.forEach(function(item){ 
   //       var total_qty = 0;
   //       total_qty +=  ((item.qty/item.packet));
   //       for (let i = 0; i < item.packet; i++) {
   //       var a = frappe.model.add_child(cur_frm.doc, "GRN Inward", "grn_inward_item_details");
   //       a.part_number = item.part_number;
   //       a.item_name = item.description;
   //       // a.purchase_order = frm.doc.purchase_order || "";
   //       a.type_of_po = frm.doc.po_type;
   //       a.qty = item.qty/item.packet;
   //       a.lot_no = item.lot_no;
   //       a.packet = i+1; 
   //     // }
   //    }
   //    //   refresh_field("grn_inward_item_details");
   //        });
   //   }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
   //   },
      on_submit: function(frm, cdt, cdn) {
      var me = this;
      var doc = frm.doc
      var print_format = "BarcodeLabesidebyside"; // print format name
      
      var w = window.open(frappe.urllib.get_full_url("/printview?"
         +"doctype="+encodeURIComponent(cdt)
         +"&name="+encodeURIComponent(cdn)
         +"&trigger_print=1"
         +"&format=" + print_format
         +"&no_letterhead=0"
         ));
      
         // if(!w) {
         //    msgprint(__("Please enable pop-ups for printing.")); return;
         // }
      },
      validate: function(frm, cdt, cdn) {
      grn_total_qty(frm, cdt, cdn);
		   refresh_field("grn_inward_item_details");
         if (frm.doc.total_inward_qty!=frm.doc.total_qty){
            frappe.msgprint(__("Part Number Total Qty Not matching with Lot Qty"));
            frappe.validated = false;
         }
         cur_frm.set_value("created_by", frappe.session.user)
      },

      on_submit: function(frm, cdt, cdn) {
         frappe.set_route("Form", "GRN Inward", "new_grn_inward");
      // var me = this;
      // var doc = frm.doc
      // var print_format = "BarcodePacketLabel"; // print format name
      
      // var w = window.open(frappe.urllib.get_full_url("/printview?"
      //    +"doctype="+encodeURIComponent(cdt)
      //    +"&name="+encodeURIComponent(cdn)
      //    +"&trigger_print=1"
      //    +"&format=" + print_format
      //    +"&no_letterhead=0"
      //    ));
      
      //    if(!w) {
      //       msgprint(__("Please enable pop-ups for printing.")); return;
      //    }
      }
      })

	cur_frm.fields_dict.purchase_order.get_query = function(doc) {
		return {
			filters: {
				supplier:cur_frm.doc.supplier,
            docstatus: 1,
            status: ["not in", ["Closed", "On Hold"]],
            per_received: ["<", 99.99],
            company: me.frm.doc.company
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
      var print_format = "BarcodeLabesidebyside"; // print format name
      
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
      frappe.ui.form.on('GRN Inward', {
         onload_post_render: function(frm) {
            frm.get_field("create_new").$input.addClass('btn-primary');
            frm.get_field("update").$input.addClass('btn-primary');
            },
           validate: function(frm) {
            if (!frm.doc.supplier){
					frappe.msgprint(__("Please select Supplier"));
					frappe.validated = false;
				};
            if (!frm.doc.supplier_invoice_no){
					frappe.msgprint(__("Please add supplier invoice details"));
					frappe.validated = false;
				};
            if (!frm.doc.supplier_invoice_date){
					frappe.msgprint(__("Please add supplier invoice details"));
					frappe.validated = false;
				};
            if (!frm.doc.main_warehouse){
					frappe.msgprint(__("Please select Main Warehouse"));
					frappe.validated = false;
				};
            // cur_frm.fields_dict.child_table_name.grid.toggle_reqd
            // ("grn_inward_item_details", 1)
           },
           refresh: function(frm) {
           cur_frm.fields_dict.main_warehouse.get_query = function(doc) {
            return {
               filters: {
                  company:frm.doc.company,
                  is_group:1
               }
            }
            }
         }
      })

      frappe.ui.form.on("GRN Inward Item Details", {
         qty: function(frm, cdt, cdn){ 
            grn_total_qty(frm, cdt, cdn);
		   refresh_field("grn_inward_item_details");
		   }
             
             });
      
      function grn_total_qty(frm, cdt, cdn) {
         // estimated_amount: function(frm, cdt, cdn) {
         var d = locals[cdt][cdn];
         var total_qty = 0;
         var total_inward_qty = 0;
         frm.doc.grn_inward_item_details.forEach(function(d) { total_qty += d.qty});
         frm.set_value('total_qty', total_qty);
         frm.doc.grn_inward_item.forEach(function(d) { total_inward_qty += d.qty});
         frm.set_value('total_inward_qty', total_inward_qty);
             }	
      // frappe.ui.form.on("GRN Inward", {
      //    validate: function(frm) {
      //        if (frm.doc.__islocal) {
      //       if(frm.doc.docstatus<2){
      //       frappe.call({
      //          "method": "frappe.client.get",
      //          "args": {
      //             "doctype": "GRN Inward",
      //             fieldname: "supplier_invoice_no",
      //             filters: { supplier_invoice_no: frm.doc.supplier_invoice_no, supplier: frm.doc.supplier, docstatus: ["!=", "2"]},
               
      //          },
      //          "callback": function(response) {
      //             var sinv = response.message;
      
      //             if (sinv) {
      //                frappe.msgprint("GRN is Already Exists for this supplier Invoice " + sinv.name + sinv.supplier);
      //                frappe.validated=false;
      //             } else {
                      
      //                frappe.validated=True;				
                      
      //             }
      //          }
      //       });
      //    }
      //    }
      // }});
  