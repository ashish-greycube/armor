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
		select
			tso.name, tso.customer_name , tso.customer_group , tcic.model, tsoi.item_name , tso.transaction_date , 
			tsoi.delivery_date , tso.branch_cf , tu.full_name 
		from `tabSales Order` tso 
		left outer join `tabCar Information CT` tcic on tcic.parent = tso.name 
		inner join `tabSales Order Item` tsoi on tsoi.parent = tso.name 
		inner join tabUser tu on tu.name = tso.owner 
				{conditions}
		order by tso.name, tso.transaction_date
        """.format(conditions=conditions), filters)

    return data


def get_columns(filters):
    columns = [
        {
            "label": _("Sales order"),
            "fieldtype": "Link",
            "fieldname": "name",
            "options": "Sales order",
            "width": 200
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
            "label": _("Model"),
            "fieldname": "model",
            "width": 220
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "width": 220
        },
        {
            "label": _("Transaction Date"),
            "fieldtype": "Date",
            "fieldname": "transaction_date",
            "width": 120
        },
        {
            "label": _("Delivery Date"),
            "fieldtype": "Date",
            "fieldname": "delivery_date",
            "width": 120
        },
        {
            "label": _("Branch"),
            "fieldtype": "Data",
            "fieldname": "branch_cf",
            "width": 150
        },
        {
            "label": _("Created By"),
            "fieldtype": "Link",
            "fieldname": "owner",
            "options": "User",
            "width": 120
        },
    ]

    return columns


def get_conditions(filters):
    conditions = []

    if filters.from_date:
        conditions.append("tso.transaction_date >= %(from_date)s")
    if filters.to_date:
        conditions.append("tso.transaction_date <= %(to_date)s")

    if filters.branch:
        conditions.append("tso.branch_cf <= %(branch)s")
    if filters.owner:
        conditions.append("tso.owner = %(owner)s")

    return conditions and " where " + " and ".join(conditions) or ""
