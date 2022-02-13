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
            tpe.name, tpe.posting_date ,  tpe.mode_of_payment , tpe.paid_amount , 
            tper.reference_doctype, tper.reference_name, coalesce(tso.branch_cf,tsi.branch_cf) batch
        from 
            `tabPayment Entry` tpe 
            inner join `tabPayment Entry Reference` tper on tper.parent = tpe.name
            left outer join `tabSales Invoice` tsi on tper.reference_doctype = 'Sales Invoice' and tsi.name = tper.reference_name 
            left outer join `tabSales Order` tso on tper.reference_doctype = 'Sales Order' and tso.name = tper.reference_name 
        {conditions}
        order by tpe.name, tper.reference_doctype, tper.reference_name
        """.format(conditions=conditions), filters)

    return data


def get_columns(filters):
    columns = [
        {
            "label": _("Payment Entry"),
            "fieldtype": "Link",
            "fieldname": "name",
            "options": "Payment Entry",
            "width": 200
        },
        {
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "fieldname": "posting_date",
            "width": 120
        },
        {
            "label": _("Mode of Payment"),
            "fieldtype": "Data",
            "fieldname": "mode_of_payment",
            "width": 150
        },
        {
            "label": _("Paid Amount"),
            "fieldtype": "Currency",
            "fieldname": "paid_amount",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("Reference Type"),
            "fieldname": "reference_doctype",
            "width": 150
        },
        {
            "label": _("Reference Name"),
            "fieldtype": "Link",
            "fieldname": "reference_name",
            "options": "Sales Invoice",
            "width": 180
        },
        {
            "label": _("Branch"),
            "fieldname": "branch",
            "width": 180
        }
    ]

    return columns


def get_conditions(filters):
    conditions = ["where tpe.payment_type = 'Receive'"]

    if filters.from_date:
        conditions.append("tpe.posting_date >= %(from_date)s")
    if filters.to_date:
        conditions.append("tpe.posting_date <= %(to_date)s")
    if filters.mode_of_payment:
        conditions.append("tpe.mode_of_payment <= %(mode_of_payment)s")
    if filters.branch:
        conditions.append(
            "coalesce(tsi.branch_cf, tso.branch_cf) = %(branch)s")
    if filters.created_by:
        conditions.append("tpe.owner >= %(created_by)s")

    return conditions and " and ".join(conditions) or ""
