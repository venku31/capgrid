// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cycle Count Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"location",
			"label": __("Location"),
			"fieldtype": "Link",
			"options": "Warehouse Location"
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
		
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		// console.log(data.lot_location);
		if (data.location != data.lot_location) {
			value = "<span style='color:red'>" + value + "</span>";
			// value = `<span style='color:#ff8c00';> </span>`;
		}
		

		return value;
	},
}