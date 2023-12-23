// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["GL Entry and Purchase Invoice Difference"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
		}
		// {
		// 	"fieldname":"company",
		// 	"label": __("Company"),
		// 	"fieldtype": "Link",
		// 	"options": "Company",
		// 	"default": frappe.defaults.get_user_default("Company")
		// }
		
	],
	// "formatter": function (value, row, column, data, default_formatter) {
	// 	value = default_formatter(value, row, column, data);
	// 	// console.log(data.lot_location);
	// 	if (data.difference != 0) {
	// 		value = "<span style='color:red'>" + value + "</span>";
	// 		// value = `<span style='color:#ff8c00';> </span>`;
	// 	}
		

	// 	return value;
	// },
}