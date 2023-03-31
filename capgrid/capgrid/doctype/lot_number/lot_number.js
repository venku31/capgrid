// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lot Number', {
	before_save(frm) {
		if(frm.doc.parent_lot && frm.doc.__islocal) {
		frm.set_value("naming_series","parent_lot.-.##");
		}
	  }
});
