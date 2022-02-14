// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Armor Payment"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "mode_of_payment",
			"fieldtype": "Link",
			"label": "Mode of Payment",
			"options": "Mode of Payment",
		},
		{

			"fieldname": "payment_type",
			"fieldtype": "Select",
			"label": "Payment Type",
			"options": "\nReceive\nPay",
			"default": "Receive"
		}

	],


	"formatter": function (value, row, column, data, default_formatter) {

		value = default_formatter(value, row, column, data);
		if (column.id == 'reference_name' && data.reference_doctype !== "Sales Invoice") {
			value = value.replace('sales-invoice', frappe.scrub(data.reference_doctype)).replace('_', '-');
			// console.log(value);
		}

		return value;
	},

};
