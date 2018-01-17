<h3>{{_("Resource Booking")}}</h3>

<br>{{_("Subject")}}: {{ doc.subject }}
<p>{{ doc.description }}</p>

<h4>{{_("Details")}}</h4>
{{_("Resource Booking Name")}}: {{ frappe.utils.get_link_to_form(doc.doctype, doc.name) }}

<br>{{_("Start Time")}}: 
    {% if(doc.repeat_on != 'Every Day') %} 
        {{ doc.starts_on }} 
    {% else %}
        {{ frappe.utils.format_datetime(doc.starts_on, "hh:mm") }}
    {% endif %}

<br>{{_("End Time")}}: 
     {% if(doc.repeat_on != 'Every Day') %} 
        {{ doc.ends_on }} 
    {% else %}
        {{ frappe.utils.format_datetime(doc.ends_on, "hh:mm") }}
    {% endif %}

{% if(doc.repeat_on) %}
    <br>
    <br>{{_("Repeat On")}}:
    {% if(doc.repeat_on != 'Every Day') %} 
        {{ doc.repeat_on }}
    {% else %}
        {% if(doc.monday) %}
            &nbsp;{{_("Monday")}}
        {% endif %}
        {% if(doc.tuesday) %}
            &nbsp;{{_("Tuesday")}}
        {% endif %}
        {% if(doc.wednesday) %}
            &nbsp;{{_("Wednesday")}}
        {% endif %}
        {% if(doc.thursday) %}
            &nbsp;{{_("Thursday")}}
        {% endif %}
        {% if(doc.friday) %}
            &nbsp;{{_("Friday")}}
        {% endif %}
        {% if(doc.saturday) %}
            &nbsp;{{_("Saturday")}}
        {% endif %}
        {% if(doc.sunday) %}
            &nbsp;{{_("Sunday")}}
        {% endif %}
    {% endif %}
    {% if(doc.repeat_till) %}
      <br>{{_("Repeat Till")}}: {{ doc.repeat_till }}
    {% endif %}
{% endif %}
