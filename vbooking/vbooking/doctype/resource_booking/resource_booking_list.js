frappe.listview_settings['Resource Booking'] = {
	add_fields: ["starts_on", "ends_on"],
	onload: function(listview) {
		listview.page.clear_user_actions();
		listview.page.add_menu_item(__("Event"), function() {
			frappe.set_route("List", 'Resource Booking', "Calendar");
		});

	}
}