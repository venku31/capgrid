// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lot Number Generation', {
         validate: function(frm) {
            if (!frm.doc.supplier){
					frappe.msgprint(__("Please select Supplier"));
					frappe.validated = false;
				};
            if (!frm.doc.main_warehouse){
					frappe.msgprint(__("Please select Main Warehouse"));
					frappe.validated = false;
				};
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
              
         },
         before_cancel: function(frm) {
				frappe.msgprint(__("Please Cancel Stock Entry"));
				frappe.validated = false;
				
         },
         on_submit: function(frm, cdt, cdn) {
            var me = this;
            var doc = frm.doc
            var print_format = "BarcodeLabelExisting"; // print format name
            
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
});

frappe.ui.form.on("Lot Number Generation Item", {
   packet: function(frm, cdt, cdn){ 
      var item = locals[cdt][cdn];
      cur_frm.clear_table("lot_no_generate_item_details");
      frm.doc.lot_no_generate_item.forEach(function(item){ 
         var total_qty = 0;
         total_qty +=  ((item.qty/item.packet));
         for (let i = 0; i < item.packet; i++) {
      var a = frappe.model.add_child(cur_frm.doc, "GRN Inward", "lot_no_generate_item_details");
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
       frm.save();
       }
       });
   frappe.ui.form.on('Lot Number Generation', {
      validate: function(frm, cdt, cdn) {
         grn_total_qty(frm, cdt, cdn);
            refresh_field("lot_no_generate_item_details");
            if (frm.doc.total_inward_qty!=frm.doc.total_qty){
               frappe.msgprint(__("Part Number Total Qty Not matching with Lot Qty"));
               frappe.validated = false;
            }
            cur_frm.set_value("created_by", frappe.session.user)
         },
      })

   frappe.ui.form.on("Lot Number Generation Item Details", {
         qty: function(frm, cdt, cdn){ 
            grn_total_qty(frm, cdt, cdn);
		   refresh_field("lot_no_generate_item_details");
		   }
             
             });
      
      function grn_total_qty(frm, cdt, cdn) {
         // estimated_amount: function(frm, cdt, cdn) {
         var d = locals[cdt][cdn];
         var total_qty = 0;
         var total_inward_qty = 0;
         frm.doc.lot_no_generate_item_details.forEach(function(d) { total_qty += d.qty});
         frm.set_value('total_qty', total_qty);
         frm.doc.lot_no_generate_item.forEach(function(d) { total_inward_qty += d.qty});
         frm.set_value('total_inward_qty', total_inward_qty);
             }	