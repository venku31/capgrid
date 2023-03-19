import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.report.financial_statements import (
	get_columns,
	get_data,
	get_filtered_list_for_consolidated_report,
	get_period_list,
	get_accounts,
	filter_accounts
)


def execute(filters=None):
	period_list = get_period_list(
		filters.from_fiscal_year,
		filters.to_fiscal_year,
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		company=filters.company,
	)

	income = []
	expense = []
	final_expense = []
	final_income = []
	parent_company = filters.company
	if frappe.db.get_value('Company',filters.company,'is_group'):
		child_comp_list = frappe.db.get_list('Company',{'parent_company':filters.company})
		final_income = get_data(
				parent_company,
				"Income",
				"Credit",
				period_list,
				filters=filters,
				accumulated_values=filters.accumulated_values,
				ignore_closing_entries=True,
				ignore_accumulated_values_for_fy=True,
			)
		final_expense = get_data(
			parent_company,
			"Expense",
			"Debit",
			period_list,
			filters=filters,
			accumulated_values=filters.accumulated_values,
			ignore_closing_entries=True,
			ignore_accumulated_values_for_fy=True,)
		
		for comp in child_comp_list:

			company = comp['name']
			filters.company = comp['name']

			income = get_data(
				company,
				"Income",
				"Credit",
				period_list,
				filters=filters,
				accumulated_values=filters.accumulated_values,
				ignore_closing_entries=True,
				ignore_accumulated_values_for_fy=True,
			)
			expense = get_data(
				company,
				"Expense",
				"Debit",
				period_list,
				filters=filters,
				accumulated_values=filters.accumulated_values,
				ignore_closing_entries=True,
				ignore_accumulated_values_for_fy=True,
			)
			{'account_name': 'Total Income (Credit)', 'account': 'Total Income (Credit)', 'currency': 'INR', 'opening_balance': 0.0, 'apr_2022': 0.0, 'may_2022': 0.0, 'jun_2022': 0.0, 'jul_2022': 0.0, 'aug_2022': 0.0, 'sep_2022': 0.0, 'oct_2022': 0.0, 'nov_2022': 0.0, 'dec_2022': 0.0, 'jan_2023': 0.0, 'feb_2023': 0.0, 'mar_2023': 0.0, 'total': 0.0}
			{'account': 'Indirect Income - TE', 'parent_account': 'Income - TE', 'indent': 1.0, 'year_start_date': '2022-04-01', 'year_end_date': '2023-03-31', 'currency': 'INR', 'include_in_gross': 0, 'account_type': '', 'is_group': 1, 'opening_balance': -0.0, 'account_name': 'Indirect Income', 'apr_2022': 0.0, 'may_2022': 0.0, 'jun_2022': 0.0, 'jul_2022': 0.0, 'aug_2022': 0.0, 'sep_2022': 0.0, 'oct_2022': 0.0, 'nov_2022': 0.0, 'dec_2022': 0.0, 'jan_2023': 0.0, 'feb_2023': 0.0, 'mar_2023': 0.0, 'has_value': False, 'total': 0}
			for inc in final_income:
				for child_inc in income:
					if inc and child_inc:
						if inc['account_name'] == child_inc['account_name']:
							for key in child_inc.keys():
								if key not in ['account_name','account', 'parent_account', 'indent', 'year_start_date', 'year_end_date', 'currency', 'account_type', 'is_group']:
									inc[key]+=child_inc[key]
			for exp in final_expense:
				for child_exp in expense:
					if exp and child_exp:
						if exp['account_name'] == child_exp['account_name']:
							for key in child_exp.keys():
								if key not in ['account_name','account', 'parent_account', 'indent', 'year_start_date', 'year_end_date', 'currency', 'account_type', 'is_group']:
									exp[key]+=child_exp[key]
					
			
	else:
		income = get_data(
				filters.company,
				"Income",
				"Credit",
				period_list,
				filters=filters,
				accumulated_values=filters.accumulated_values,
				ignore_closing_entries=True,
				ignore_accumulated_values_for_fy=True,
			)

		expense = get_data(
			filters.company,
			"Expense",
			"Debit",
			period_list,
			filters=filters,
			accumulated_values=filters.accumulated_values,
			ignore_closing_entries=True,
			ignore_accumulated_values_for_fy=True,
		)

	if final_expense and final_income:
		income = final_income
		expense = final_expense
	net_profit_loss = get_net_profit_loss(
		income, expense, period_list, filters.company, filters.presentation_currency
	)

	data = []
	data.extend(income or [])
	data.extend(expense or [])
	if net_profit_loss:
		data.append(net_profit_loss)

	columns = get_columns(
		filters.periodicity, period_list, filters.accumulated_values, filters.company
	)

	chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

	currency = filters.presentation_currency or frappe.get_cached_value(
		"Company", filters.company, "default_currency"
	)
	report_summary = get_report_summary(
		period_list, filters.periodicity, income, expense, net_profit_loss, currency, filters
	)

	return columns, data, None, chart, report_summary


def get_report_summary(
	period_list, periodicity, income, expense, net_profit_loss, currency, filters, consolidated=False
):
	net_income, net_expense, net_profit = 0.0, 0.0, 0.0

	# from consolidated financial statement
	if filters.get("accumulated_in_group_company"):
		period_list = get_filtered_list_for_consolidated_report(filters, period_list)

	for period in period_list:
		key = period if consolidated else period.key
		if income:
			net_income += income[-2].get(key)
		if expense:
			net_expense += expense[-2].get(key)
		if net_profit_loss:
			net_profit += net_profit_loss.get(key)

	if len(period_list) == 1 and periodicity == "Yearly":
		profit_label = _("Profit This Year")
		income_label = _("Total Income This Year")
		expense_label = _("Total Expense This Year")
	else:
		profit_label = _("Net Profit")
		income_label = _("Total Income")
		expense_label = _("Total Expense")

	return [
		{"value": net_income, "label": income_label, "datatype": "Currency", "currency": currency},
		{"type": "separator", "value": "-"},
		{"value": net_expense, "label": expense_label, "datatype": "Currency", "currency": currency},
		{"type": "separator", "value": "=", "color": "blue"},
		{
			"value": net_profit,
			"indicator": "Green" if net_profit > 0 else "Red",
			"label": profit_label,
			"datatype": "Currency",
			"currency": currency,
		},
	]


def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Profit for the year") + "'",
		"account": "'" + _("Profit for the year") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0

		net_profit_loss[key] = total_income - total_expense

		if net_profit_loss[key]:
			has_value = True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss


def get_chart_data(filters, columns, income, expense, net_profit_loss):
	labels = [d.get("label") for d in columns[2:]]

	income_data, expense_data, net_profit = [], [], []

	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[-2].get(p.get("fieldname")))
		if net_profit_loss:
			net_profit.append(net_profit_loss.get(p.get("fieldname")))

	datasets = []
	if income_data:
		datasets.append({"name": _("Income"), "values": income_data})
	if expense_data:
		datasets.append({"name": _("Expense"), "values": expense_data})
	if net_profit:
		datasets.append({"name": _("Net Profit/Loss"), "values": net_profit})

	chart = {"data": {"labels": labels, "datasets": datasets}}

	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	chart["fieldtype"] = "Currency"

	return chart