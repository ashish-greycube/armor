# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):

    conditions = get_conditions(filters)

    data = frappe.db.sql(
        """
			with fn as
			(
					select 
						tsi.name, tsi.posting_date, tsi.customer_name, tsi.customer_group , 
						tsi.sales_partner , det.warehouse , 
						tsi.base_net_total , det.nhours, det.cogs, det.cost_of_labor,
						coalesce(det.cogs,0) + coalesce(det.cost_of_labor,0) total_cost, 
                        tsi.base_net_total - coalesce(det.cogs,0) - coalesce(det.cost_of_labor,0) net_profit,
						case when tsi.base_net_total > 0 
						then 100 * (tsi.base_net_total - coalesce(det.cogs,0) - coalesce(det.cost_of_labor,0))/tsi.base_net_total 
						else 0 end proft_pct
					from `tabSales Invoice` tsi 
					inner join (
						select tsii.parent , sum(tge.debit) cogs, sum(tdni.qty) nhours, sum(tdni.qty*tdni.rate_per_hour_cf) cost_of_labor, 
						CONCAT_WS(',',tsii.warehouse) warehouse
						from `tabSales Invoice Item` tsii
						left outer join `tabSales Order Item` tsoi on tsoi.parent = tsii.sales_order 
						left outer join `tabDelivery Note Item` tdni on tdni.so_detail = tsoi.name
						left outer join `tabGL Entry` tge on tge.voucher_no = tdni.parent and tdni.expense_account = tge.account 
						group by tsii.parent
					) det on det.parent = tsi.name
			        {conditions}
			)
			select * from fn
			union all 
			select '', '', '', '','','', sum(fn.base_net_total), sum(fn.nhours), sum(fn.cogs), sum(fn.cost_of_labor),
			sum(fn.total_cost), sum(fn.net_profit), avg(fn.proft_pct) 
			from fn
        """.format(conditions=conditions), filters)

    return data


def get_columns(filters):
    columns = [
        {
            "label": _("Sales Invoice"),
            "fieldtype": "Link",
            "fieldname": "name",
            "options": "Sales Invoice",
            "width": 200
        },
        {
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "fieldname": "posting_date",
            "width": 120
        },
        {
            "label": _("Customer"),
            "fieldtype": "Link",
            "fieldname": "customer_name",
            "options": "Customer",
            "width": 220
        },
        {
            "label": _("Customer Group"),
            "fieldname": "customer_group",
            "width": 220
        },
        {
            "label": _("Sales Partner"),
            "fieldname": "sales_partner",
            "width": 220
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "width": 220
        },
        {
            "label": _("Net Total"),
            "fieldtype": "Currency",
            "fieldname": "base_net_total",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("Number of Hours"),
            "fieldtype": "Float",
            "fieldname": "qty",
            "width": 120
        },
        {
            "label": _("Cost of Materials"),
            "fieldtype": "Currency",
            "fieldname": "cogs",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("Cost of Labor"),
            "fieldtype": "Currency",
            "fieldname": "cost_of_labor",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("Total Cost"),
            "fieldtype": "Currency",
            "fieldname": "total_cost",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("Profit"),
            "fieldtype": "Currency",
            "fieldname": "net_profit",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("Profit Percent"),
            "fieldtype": "Percent",
            "fieldname": "profit_pct",
            "width": 120
        },
    ]

    return columns


def get_conditions(filters):
    conditions = []

    if filters.from_date:
        conditions.append("tsi.posting_date >= %(from_date)s")
    if filters.to_date:
        conditions.append("tsi.posting_date <= %(to_date)s")

    if filters.warehouse:
        conditions.append("det.warehouse like  '%%%(warehouse)s%%")
    if filters.sales_partner:
        conditions.append("tsi.sales_partner = %(sales_partner)s")
    if filters.customer:
        conditions.append("tsi.customer <= %(customer)s")

    return conditions and " where " + " and ".join(conditions) or ""
