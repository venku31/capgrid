// Copyright (c) 2023, Capgrid Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('WMS Settings', {
	refresh: function(frm) {
		cur_frm.fields_dict['wms_settings_details'].grid.get_field('main_warehouse').get_query = function(doc, cdt, cdn) {
			var d = locals[cdt][cdn]
			return {
				filters: [
					['Warehouse', 'is_group', '=', '1'],
					['Warehouse', 'company', '=', d.company]
				]
			}
		}
		cur_frm.fields_dict['wms_settings_details'].grid.get_field('inward_warehouse').get_query = function(doc, cdt, cdn) {
			var d = locals[cdt][cdn]
			return {
				filters: [
					['Warehouse', 'parent_warehouse', '=', d.main_warehouse],
					['Warehouse', 'company', '=', d.company]
				]
			}
		}
		cur_frm.fields_dict['wms_settings_details'].grid.get_field('rejected_warehouse').get_query = function(doc, cdt, cdn) {
			var d = locals[cdt][cdn]
			return {
				filters: [
					['Warehouse', 'parent_warehouse', '=', d.main_warehouse],
					['Warehouse', 'company', '=', d.company]
				]
			}
		}
		cur_frm.fields_dict['wms_settings_details'].grid.get_field('quality_inspection_warehouse').get_query = function(doc, cdt, cdn) {
			var d = locals[cdt][cdn]
			return {
				filters: [
					['Warehouse', 'parent_warehouse', '=', d.main_warehouse],
					['Warehouse', 'company', '=', d.company]
				]
			}
		}
		cur_frm.fields_dict['wms_settings_details'].grid.get_field('hold_warehouse').get_query = function(doc, cdt, cdn) {
			var d = locals[cdt][cdn]
			return {
				filters: [
					['Warehouse', 'parent_warehouse', '=', d.main_warehouse],
					['Warehouse', 'company', '=', d.company]
				]
			}
		}
		cur_frm.fields_dict['wms_settings_details'].grid.get_field('temporary_location').get_query = function(doc, cdt, cdn) {
			var d = locals[cdt][cdn]
			return {
				filters: [
					['Warehouse Location', 'main_warehouse', '=', d.main_warehouse],
					['Warehouse Location', 'company', '=', d.company]
				]
			}
		}
	}
});
