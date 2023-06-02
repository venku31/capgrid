// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Lot-Wise Balance History"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				let company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						"company": company
					}
				};
			}
		},
		{
			"fieldname":"lot_number",
			"label": __("Lo No"),
			"fieldtype": "Link",
			"options": "Lot Number",
			// "get_query": function() {
			// 	let item_code = frappe.query_report.get_filter_value('item_code');
			// 	return {
			// 		filters: {
			// 			"item": item_code
			// 		}
			// 	};
			// }
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		if (column.fieldname == "Lot" && data && !!data["Lot"]) {
			value = data["Lot"];
			column.link_onclick = "frappe.query_reports['Batch-Wise Balance History'].set_batch_route_to_stock_ledger(" + JSON.stringify(data) + ")";
		}

		value = default_formatter(value, row, column, data);
		return value;
	},
	"set_lot_route_to_stock_ledger": function (data) {
		frappe.route_options = {
			"lot_number": data["Lot"]
		};

		frappe.set_route("query-report", "Stock Ledger");
	}
}