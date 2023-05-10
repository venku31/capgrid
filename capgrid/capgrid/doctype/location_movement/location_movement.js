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
			 }
		  }
});
