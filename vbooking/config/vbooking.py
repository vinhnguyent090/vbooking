from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Resource Booking"),
			"icon": "fa fa-table",
			"items": [
				{
					"type": "doctype",
					"name": "Resource Booking",
					"label": _("Resource Booking")
				}
			]

		},
		{
			"label": _("Setting"),
			"icon": "fa fa-table",
			"items": [
				{
					"type": "doctype",
					"name": "Booking Resource",
					"label": _("Booking Resource")
				}
			]

		}
    ]        