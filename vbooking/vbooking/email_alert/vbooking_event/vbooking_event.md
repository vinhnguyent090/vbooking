<h3>{{_("Booking Event")}}</h3>

<br>{{_("Event Subject")}}: {{ doc.subject }}
<p>{{ doc.description }}</p>

<h4>{{_("Details")}}</h4>
{{_("Booking Event Name")}}: {{ frappe.utils.get_link_to_form(doc.doctype, doc.name) }}

<br>{{_("Start Time")}}: {{ doc.starts_on }}
<br>{{_("End Time")}}: {{ doc.ends_on }}
<br>
<br>{{_("Repeat On")}}: {{ doc.repeat_on }}
<br>{{_("Repeat Till")}}: {{ doc.repeat_till }}
<br>
<br>{{_("Monday")}}: {{ doc.monday }}
<br>{{_("Tuesday")}}: {{ doc.tuesday }}
<br>{{_("Wednesday")}}: {{ doc.wednesday }}
<br>{{_("Thursday")}}: {{ doc.thursday }}
<br>{{_("Friday")}}: {{ doc.friday }}
<br>{{_("Saturday")}}: {{ doc.saturday }}
<br>{{_("Sunday")}}: {{ doc.sunday }}
