// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warehouse Location Label Print', {
	refresh: function(frm) {
		cur_frm.fields_dict.warehouse.get_query = function(doc) {
            return {
               filters: {
                  company:frm.doc.company,
               }
            }
            },
            frm.add_custom_button(__("Print"), function() {
               var w = window.open("/printview?doctype=Warehouse%20Location%20Label%20Print&name=" + cur_frm.doc.name + "&trigger_print=1&format=LocationLabelPrint&no_letterhead=1&_lang=es");
   
               if(!w) {
                   frappe.msgprint(__("Please enable pop-ups")); return;
               }
                   }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
     
     },
     onload_post_render: function(frm) {
      frm.get_field("get_data").$input.addClass('btn-primary');
   
},
get_data:function(frm) {
   get_location_data(frm)  	
}
});

function get_location_data(frm) {
   console.log("1")
   frappe.call({
     "method": "capgrid.capgrid.doctype.warehouse_location_label_print.warehouse_location_label_print.get_locations",
     "args": {
      "company": frm.doc.company,
      "warehouse": frm.doc.warehouse,
      },
     callback: function (r) {
      console.log(r)
      cur_frm.clear_table("warehouse_location_label_details");
      r.message.forEach(fields => {
        var child = cur_frm.add_child("warehouse_location_label_details");
        frappe.model.set_value(child.doctype, child.name, "location", fields.name)
        frappe.model.set_value(child.doctype, child.name, "warehouse", fields.warehouse)
        frappe.model.set_value(child.doctype, child.name, "main_warehouse", fields.main_warehouse)
        });
      cur_frm.refresh_fields()
         
     }
     
   });
// cur_frm.fields_dict.my_field.$input.on("click", function(evt){

// })

}