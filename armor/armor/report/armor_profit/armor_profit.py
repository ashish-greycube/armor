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
                    select t1.si_name , t1.posting_date , t1.customer_name , t1.customer_group , t1.sales_partner , t1.warehouse ,
                    t1.base_net_total , t1.cogs , t1.nhours , t1.cost_of_labor , 
                    t1.cogs + t1.cost_of_labor total_cost ,
                    t1.base_net_total - t1.cogs -t1.cost_of_labor net_profit ,
                    case when t1.base_net_total > 0 
                        then 100 * (t1.base_net_total - t1.cogs - t1.cost_of_labor) / t1.base_net_total 
                        else 0 end profit_pct 
                    from 
                    ( 
                        select t.si_name , 
                        t.posting_date, t.customer_name, t.customer_group , t.sales_partner , t.warehouse ,
                        coalesce(max(t.base_net_total),0) base_net_total, 
                        coalesce(max(tge.debit),0) cogs , 
                        coalesce(sum(tdni.no_of_hours_cf),0) nhours , 
                        coalesce(sum(tdni.no_of_hours_cf * tdni.rate_per_hour_cf),0) cost_of_labor 
                        from 
                        (
                            select tsi.name si_name , 
                            tsi.posting_date, tsi.customer_name, tsi.customer_group , tsi.sales_partner , tsi.base_net_total ,	
                            tdni.name dn_name , concat_ws(',' , tsii.warehouse) warehouse
                            from `tabSales Invoice` tsi 
                            inner join `tabSales Invoice Item` tsii on tsii.parent = tsi.name
                            left outer join `tabSales Order Item` tsoi on tsoi.parent = tsii.sales_order 
                            left outer join `tabDelivery Note Item` tdni on tdni.so_detail = tsoi.name 
                            {conditions}
                        ) t
                        left outer JOIN  `tabDelivery Note Item` tdni on tdni.name = t.dn_name 
                        left outer join `tabGL Entry` tge on tge.voucher_no = tdni.parent and tge.account  = tdni.expense_account	
                        -- 	where 	t.si_name IN ('ACC-SINV-2022-00312') 
                        group by t.si_name
                    ) t1	
			)
			select * from fn
			union all 
			select '', '', '', '', '', '', sum(fn.base_net_total), sum(fn.nhours), sum(fn.cogs), sum(fn.cost_of_labor),
			sum(fn.total_cost), sum(fn.net_profit), avg(fn.profit_pct) 
			from fn
        """.format(
            conditions=conditions
        ),
        filters,
    )

    return data


def get_columns(filters):
    columns = [
        {
            "label": _("Sales Invoice"),
            "fieldtype": "Link",
            "fieldname": "name",
            "options": "Sales Invoice",
            "width": 200,
        },
        {
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "fieldname": "posting_date",
            "width": 120,
        },
        {
            "label": _("Customer"),
            "fieldtype": "Link",
            "fieldname": "customer_name",
            "options": "Customer",
            "width": 220,
        },
        {"label": _("Customer Group"), "fieldname": "customer_group", "width": 220},
        {"label": _("Sales Partner"), "fieldname": "sales_partner", "width": 220},
        {"label": _("Warehouse"), "fieldname": "warehouse", "width": 220},
        {
            "label": _("Net Total"),
            "fieldtype": "Currency",
            "fieldname": "base_net_total",
            "options": "currency",
            "width": 120,
        },
        {
            "label": _("Number of Hours"),
            "fieldtype": "Float",
            "fieldname": "qty",
            "width": 120,
        },
        {
            "label": _("Cost of Materials"),
            "fieldtype": "Currency",
            "fieldname": "cogs",
            "options": "currency",
            "width": 120,
        },
        {
            "label": _("Cost of Labor"),
            "fieldtype": "Currency",
            "fieldname": "cost_of_labor",
            "options": "currency",
            "width": 120,
        },
        {
            "label": _("Total Cost"),
            "fieldtype": "Currency",
            "fieldname": "total_cost",
            "options": "currency",
            "width": 120,
        },
        {
            "label": _("Profit"),
            "fieldtype": "Currency",
            "fieldname": "net_profit",
            "options": "currency",
            "width": 120,
        },
        {
            "label": _("Profit Percent"),
            "fieldtype": "Percent",
            "fieldname": "profit_pct",
            "width": 120,
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
        conditions.append("tsii.warehouse = %(warehouse)s")
    if filters.sales_partner:
        conditions.append("tsi.sales_partner = %(sales_partner)s")
    if filters.customer:
        conditions.append("tsi.customer <= %(customer)s")

    return conditions and " where " + " and ".join(conditions) or ""
