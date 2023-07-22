// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on("PickList Upload", {
  download_template() {
    let export_fields = [
      [
        // "Warehouse",
        "Part Number",
        "Plant Code",
        "Trigger Qty",
        // "Reason",
        // "Remarks",
      ],
    ];
    frappe.tools.downloadify(export_fields, null, "Pick List");

  },
refresh: function(frm) {
  		cur_frm.fields_dict.warehouse.get_query = function(doc) {
			 return {
				filters: {
				   company:frm.doc.company,
				  //  is_group:1
				}
			 }
      }}
});
