// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["QI Done And Putaway Pending"] = {
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
			"fieldname":"main_warehouse",
			"label": __("Main Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company,
						"is_group":1
					}
				};

		},
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