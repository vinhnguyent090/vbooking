// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.views.calendar["vBooking Event"] = {
	field_map: {
		"start": "starts_on",
		"end": "ends_on",
		"id": "name",
		"allDay": "all_day",
		"title": "subject",
		"status": "event_type",
		"color": "color"
	},
	style_map: {
		"Public": "success",
		"Private": "info"
	},
	get_events_method: "vbooking.vbooking.doctype.vbooking_event.vbooking_event.get_events"
}
