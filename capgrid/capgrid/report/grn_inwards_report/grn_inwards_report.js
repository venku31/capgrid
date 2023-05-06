// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.query_reports["GRN Inwards Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -0),
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
			"options": "Supplier"
		},
		{
			"fieldname":"purchase_order",
			"label": __("PO"),
			"fieldtype": "Link",
			"options": "Purchase Order",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				};
		},
	    },
	
		{
			"fieldname":"lot_number",
			"label": __("Parent LOT"),
			"fieldtype": "Link",
			"options": "Lot Number",
		// 	get_query: () => {
		// 		var company = frappe.query_report.get_filter_value('company');
		// 		return {
		// 			filters: {
		// 				'company': company
		// 			}
		// 		};

		// },
	},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		}
		
	]
}