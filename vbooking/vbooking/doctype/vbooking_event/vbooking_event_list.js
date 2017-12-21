frappe.listview_settings['vBooking Event'] = {
	add_fields: ["starts_on", "ends_on"],
	onload: function(listview) {
		listview.page.clear_user_actions();
		listview.page.add_menu_item(__("Event"), function() {
			frappe.set_route("List", 'vBooking Event', "Calendar");
		});

	}
}