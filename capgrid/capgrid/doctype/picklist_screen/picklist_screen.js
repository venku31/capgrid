// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('PickList Screen', {
	refresh: function(frm) {
		frm.set_df_property('pick_list','read_only',1)
		frm.set_df_property('customer','read_only',1)
		if(frm.doc.action) frm.set_df_property('action','read_only',1)
	}
});
