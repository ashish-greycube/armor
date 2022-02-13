// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Armor Booking"] = {
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
			"fieldname": "branch",
			"fieldtype": "Link",
			"label": "Branch",
			"options": "Branch",
		},
		{
			"fieldname": "owner",
			"fieldtype": "Link",
			"label": "Created By",
			"options": "User",
		},
	]
};
