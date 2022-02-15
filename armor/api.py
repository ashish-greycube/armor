
from __future__ import unicode_literals
import frappe
# from erpnext.setup.doctype.item_group.item_group import get_child_groups
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate, getdate
from erpnext.stock.get_item_details import get_conversion_factor
from frappe.model.mapper import get_mapped_doc
from frappe.utils import get_link_to_form
from frappe import _



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_car_model(doctype, txt, searchfield, start, page_len, filters):
	if filters and filters.get('group'):
		cond = "'%s'" % filters.get('group')
		return frappe.db.sql("""select car_model from `tabCar Group Model CT`
				where parent = {cond}
				order by name limit %(start)s, %(page_len)s"""
				.format(cond=cond), {
					'start': start, 'page_len': page_len
				})


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	conditions = []

	#Get searchfields from meta and use in Item Link field query
	meta = frappe.get_meta("Item", cached=True)
	searchfields = meta.get_search_fields()

	if "description" in searchfields:
		searchfields.remove("description")

	columns = ''
	extra_searchfields = [field for field in searchfields
		if not field in ["name", "item_group", "description"]]

	if extra_searchfields:
		columns = ", " + ", ".join(extra_searchfields)

	searchfields = searchfields + [field for field in[searchfield or "name", "item_code", "item_group", "item_name"]
		if not field in searchfields]
	searchfields = " or ".join([field + " like %(txt)s" for field in searchfields])

	description_cond = ''
	if frappe.db.count('Item', cache=True) < 50000:
		# scan description only if items are less than 50000
		description_cond = 'or tabItem.description LIKE %(txt)s'

	if filters and filters.get('armour_item_group'):
		item_group=filters.get('armour_item_group')
		item_group_list = ", ".join(['"' + i[0] + '"' for i in get_child_groups(item_group)])

	return frappe.db.sql("""select tabItem.name,
		if(length(tabItem.item_name) > 40,
			concat(substr(tabItem.item_name, 1, 40), "..."), item_name) as item_name,
		tabItem.item_group,
		if(length(tabItem.description) > 40, \
			concat(substr(tabItem.description, 1, 40), "..."), description) as description
		{columns}
		from tabItem
		where tabItem.docstatus < 2
			and tabItem.has_variants=0
			and tabItem.disabled=0
			and tabItem.is_sales_item=1
			and (item_group in ({item_group_list}))
			and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
			and ({scond} or tabItem.item_code IN (select parent from `tabItem Barcode` where barcode LIKE %(txt)s)
				{description_cond})
		
			{mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
			idx desc,
			name, item_name
		limit %(start)s, %(page_len)s """.format(
			columns=columns,
			item_group_list=item_group_list,
			scond=searchfields,
			# fcond=get_filters_cond(doctype, filters, conditions).replace('%', '%%'),
			mcond=get_match_cond(doctype).replace('%', '%%'),
			description_cond = description_cond),
			{
				"today": nowdate(),
				"txt": "%%%s%%" % txt,
				"_txt": txt.replace("%", ""),
				"start": start,
				"page_len": page_len
			}, as_dict=as_dict)



def get_child_groups(item_group_name):
	item_group = frappe.get_doc("Item Group", item_group_name)
	return frappe.db.sql("""select name
		from `tabItem Group` where lft>=%(lft)s and rgt<=%(rgt)s
			""", {"lft": item_group.lft, "rgt": item_group.rgt})				

# @frappe.whitelist()
# def make_stock_entry_from_sales_invoice(self,method):
# 	source_name=self.name
# 	target_doc=None
# 	def set_missing_values(source, target):
# 		target.stock_entry_type='Material Issue'
# 		target.purpose = 'Material Issue'

# 		for consumed_material in source.consumed_materials:
# 			product_bundle = frappe.get_doc('Product Bundle',consumed_material.product_bundle_item_code)
# 			for item in product_bundle.items:
# 				conversion_factor=get_conversion_factor(item.item_code,item.uom).get("conversion_factor", 1)
# 				qty=(item.qty)*(consumed_material.qty)
# 				target.append('items',{
# 				'item_code':item.item_code,
# 				'qty':qty,
# 				'conversion_factor' : conversion_factor	,	
# 				'transfer_qty' : qty * conversion_factor,
# 				'uom':item.uom,
# 				's_warehouse':consumed_material.warehouse
# 				})

# 		target.run_method("calculate_rate_and_amount")
# 		target.set_stock_entry_type()


# 	doclist = get_mapped_doc("Sales Invoice", source_name, {
# 		"Sales Invoice": {
# 			"doctype": "Stock Entry",
# 			"validation": {
# 				"docstatus": ["=", 1]
# 			}
# 		}
# 	}, target_doc, set_missing_values,ignore_permissions=True)

# 	doclist.save(ignore_permissions=True)
# 	frappe.msgprint(_("Stock Entry {0} is created from sales invoice {1} .".format(get_link_to_form('Stock Entry',doclist.name),frappe.bold(source_name))))
# 	return 				

@frappe.whitelist()
def create_sales_order_and_customer(source_name, target_doc=None,ignore_permissions=True):
	customer=_make_customer(source_name, target_doc,ignore_permissions)
	frappe.msgprint(_("Customer {0} is created.").format(customer), alert=True)
	def set_missing_values(source, target):
		target.customer=customer
		target.order_type='Sales'
		if source.guest_group_cf:
			target.customer_group=source.guest_group_cf
			max_discount_allowed_cf=frappe.db.get_value('Customer Group', source.guest_group_cf, 'max_discount_allowed_cf')
			if max_discount_allowed_cf:
				target.max_discount_allowed_cf=max_discount_allowed_cf

	doclist = get_mapped_doc("Lead", source_name, {
		"Lead": {
			"doctype": "Sales Order",
		}}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)
	doclist.run_method('set_missing_values')
	return doclist


def _make_customer(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		if source.company_name:
			target.customer_type = "Company"
			target.customer_name = source.company_name
		else:
			target.customer_type = "Individual"
			target.customer_name = source.lead_name
		# target.phone_number_cf=source.phone
		target.customer_group = source.guest_group_cf or frappe.db.get_default("Customer Group")

	doclist = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Customer",
			"field_map": {
				"name": "lead_name",
				"company_name": "customer_name",
			"contact_no": "phone_1",
				"fax": "fax_1"
			}
		}}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)
	doclist.save()
	return doclist.name	


def update_car_information_in_sales_order(self,method):
	sales_order_name=None
	if self.items:
		for item in self.items:
			if item.against_sales_order:
				sales_order_name=item.against_sales_order	
				if sales_order_name:
					break
	print('sales_order_name'*100,sales_order_name)
	if sales_order_name:
		sales_order=frappe.get_doc('Sales Order',sales_order_name)
		for delivery_cars in self.cars:
			for so_cars in sales_order.cars:
				if delivery_cars.model == so_cars.model:
					frappe.db.set_value('Car Information CT', so_cars.name, 'color', delivery_cars.color)
					frappe.db.set_value('Car Information CT', so_cars.name, 'km', delivery_cars.km)
					frappe.db.set_value('Car Information CT', so_cars.name, 'plate_no', delivery_cars.plate_no)
					break
