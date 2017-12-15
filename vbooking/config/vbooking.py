from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Booking Resource"),
			"icon": "fa fa-table",
			"items": [
				{
					"type": "doctype",
					"name": "vBooking Event",
					"label": _("Booking Event")
				}
			]

		},
		{
			"label": _("Setting"),
			"icon": "fa fa-table",
			"items": [
				{
					"type": "doctype",
					"name": "vBooking Resource",
					"label": _("Booking Resource")
				}
			]

		}
    ]        