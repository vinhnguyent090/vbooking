# -*- coding: utf-8 -*-
# Copyright (c) 2017, vinhnguyen.t090@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six.moves import range
from six import string_types
import frappe
import json
from frappe import _

from frappe.model.document import Document
from frappe.utils.user import get_enabled_system_users
from frappe.desk.reportview import get_filters_cond
from frappe.utils import (getdate, cint, add_months, date_diff, add_days, add_years,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from frappe.utils.background_jobs import enqueue

from erpnext.hr.doctype.employee.employee import get_employee_emails



weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
max_repeat_till = add_years(nowdate(), 1)

class vBookingEvent(Document):
	
	def validate(self):

		self.employee_emails = ', '.join(get_employee_emails([d.employee
			for d in self.employees]))

		if not self.starts_on:
			self.starts_on = now_datetime()

		if self.starts_on and self.ends_on and get_datetime(self.starts_on) > get_datetime(self.ends_on):
			frappe.msgprint(frappe._("Event end must be after start"), raise_exception=True)

		if self.starts_on == self.ends_on:
			# this scenario doesn't make sense i.e. it starts and ends at the same second!
			self.ends_on = None

		if getdate(self.starts_on) != getdate(self.ends_on) and self.repeat_on == "Every Day":
			frappe.msgprint(frappe._("Every day events should finish on the same day."), raise_exception=True)
		
		""" check date """
		if self.vbooking_resource:
			self.validate_date()

		#events = get_events(self.starts_on, self.ends_on)
		#frappe.msgprint(str(result))

	def validate_date(self):

		def add_event(e, date):
			new_event = e.copy()

			enddate = add_days(date,int(date_diff(e.ends_on.split(" ")[0], e.starts_on.split(" ")[0]))) \
				if (e.starts_on and e.ends_on) else date
			new_event.starts_on = date + " " + e.starts_on.split(" ")[1]
			if e.ends_on:
				new_event.ends_on = enddate + " " + e.ends_on.split(" ")[1]
			add_events.append(new_event)

		def get_repeat_events(e):
			if e.repeat_this_event:
				e.starts_on = get_datetime_str(e.starts_on)
				if e.ends_on:
					e.ends_on = get_datetime_str(e.ends_on)

				event_start, time_str = get_datetime_str(e.starts_on).split(" ")
				if cstr(e.repeat_till) == "":
					repeat = max_repeat_till
				else:
					repeat = e.repeat_till
				if e.repeat_on=="Every Year":
					start_year = cint(start.split("-")[0])
					end_year = cint(end.split("-")[0])
					event_start = "-".join(event_start.split("-")[1:])

					# repeat for all years in period
					for year in range(start_year, end_year+1):
						date = str(year) + "-" + event_start
						if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) and getdate(date) <= getdate(repeat):
							add_event(e, date)

					remove_events.append(e)

				if e.repeat_on=="Every Month":
					date = start.split("-")[0] + "-" + start.split("-")[1] + "-" + event_start.split("-")[2]

					# last day of month issue, start from prev month!
					try:
						getdate(date)
					except ValueError:
						date = date.split("-")
						date = date[0] + "-" + str(cint(date[1]) - 1) + "-" + date[2]

					start_from = date
					for i in range(int(date_diff(end, start) / 30) + 3):
						if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) \
							and getdate(date) <= getdate(repeat) and getdate(date) >= getdate(event_start):
							add_event(e, date)
						date = add_months(start_from, i+1)

					remove_events.append(e)

				if e.repeat_on=="Every Week":
					weekday = getdate(event_start).weekday()
					# monday is 0
					start_weekday = getdate(start).weekday()

					# start from nearest weeday after last monday
					date = add_days(start, weekday - start_weekday)

					for cnt in range(int(date_diff(end, start) / 7) + 3):
						if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) \
							and getdate(date) <= getdate(repeat) and getdate(date) >= getdate(event_start):
							add_event(e, date)

						date = add_days(date, 7)

					remove_events.append(e)

				if e.repeat_on=="Every Day":
					for cnt in range(date_diff(end, start) + 1):
						date = add_days(start, cnt)
						if getdate(date) >= getdate(event_start) and getdate(date) <= getdate(end) \
							and getdate(date) <= getdate(repeat) and e[weekdays[getdate(date).weekday()]]:
							add_event(e, date)
					remove_events.append(e)

		
		start = self.starts_on
		end = self.ends_on

		if self.repeat_this_event:
			if cstr(self.repeat_till) == "":
				end = max_repeat_till
			else:
				end = self.repeat_till

		# process recurring events
		start = start.split(" ")[0]
		end = end.split(" ")[0]
		
		filter_condition = ""
		if self.name:
			filter_condition += " and name != '%s'" % self.name
		if self.vbooking_resource:
			filter_condition += " and vbooking_resource = '%s'" % self.vbooking_resource

		query = """
		select name, subject,
			starts_on, ends_on, all_day, repeat_this_event, repeat_on,repeat_till,
			monday, tuesday, wednesday, thursday, friday, saturday, sunday, booked_by
		from `tabvBooking Event` where ((
			(starts_on between %(start)s and %(end)s)
			or (ends_on between %(start)s and %(end)s)
			or (starts_on <= %(start)s and ends_on >= %(end)s)
		) or (
			starts_on <= %(start)s and repeat_this_event=1 and
			ifnull(repeat_till, %(end)s) > %(start)s
		)) {filter_condition}""".format(filter_condition= filter_condition)

		
		# get another events
		events = frappe.db.sql(query, {
			"start": start,
			"end": end,
		}, as_dict=1)

		add_events = []
		remove_events = []

		for e in events:
			get_repeat_events(e)

		for e in remove_events:
			events.remove(e)

		events =  events + add_events
		
		if(len(events)==0):
			return None

		# get self events
		self_events = []
		self_event = frappe._dict({
			'name' : self.name,
			'subject' : self.subject,
			'starts_on' : self.starts_on,
			'ends_on' : self.ends_on,
			'all_day' : self.all_day,
			'repeat_this_event' : self.repeat_this_event,
			'repeat_on' : self.repeat_on,
			'repeat_till' : self.repeat_till,
			'monday' : self.monday,
			'tuesday' : self.tuesday,
			'wednesday' : self.wednesday,
			'thursday' : self.thursday,
			'friday' : self.friday,
			'saturday' : self.saturday,
			'sunday' : self.sunday,
			'booked_by' : self.booked_by,
		})
		self_events.append(self_event)

		add_events = []
		remove_events = []

		get_repeat_events(self_event)
		for e in remove_events:
			self_events.remove(e)

		self_events =  self_events + add_events

		# check self_events in events
		result = None
		for e in self_events:
			if result is not None:
				break
			for f in events:
				if ( get_datetime(f.starts_on) <=  get_datetime(e.starts_on) <  get_datetime(f.ends_on)) \
				or ( get_datetime(f.starts_on) <  get_datetime(e.ends_on) <=  get_datetime(f.ends_on)):
					result = f
					break

		#frappe.msgprint(str(self_events))

		if result is not None:
			employee_name = None
			if result.booked_by:
				employee_name = frappe.db.get_value("Employee", result.booked_by, "employee_name")
			frappe.throw(frappe._("{0} is booked by {1}").format(result.subject, employee_name))
		
		return result

def get_employee_name(self):
		self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
		return self.employee_name

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	return """(`tabvBooking Event`.event_type='Public' or `tabvBooking Event`.owner='%(user)s')""" % {
			"user": frappe.db.escape(user),
			"roles": "', '".join([frappe.db.escape(r) for r in frappe.get_roles(user)])
		}

def has_permission(doc, user):
	if doc.event_type=="Public" or doc.owner==user:
		return True

	return False

@frappe.whitelist()
def send_event_digest(doc, user):
	
	today = nowdate()
	events = get_events(today, today, True, for_reminder=True)

	send_events = {}
	send_emails = []
	if events:
		for e in events:
			e.starts_on = format_datetime(e.starts_on, 'hh:mm a')
			#if e.all_day:
			#	e.starts_on = "All Day"
			if e.employee_emails:
				employee_emails = e.employee_emails.split(',')
				for email in employee_emails:
					if email not in send_emails:
						send_emails.append(email)
	if send_emails:
		for email in send_emails:
			for e in events:
				if email in e.employee_emails:
					if not send_events.get(email):
						send_events[email] = []
					send_events[email].append(e)
			if send_events.get(email):
				frappe.sendmail(
					recipients= email,
					subject=frappe._("Upcoming Booking Events for Today"),
					template="upcoming_events",
					args={
						'events': events,
					},
					header=[frappe._("Events in Today's Calendar"), 'blue']
				)
				#enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)


@frappe.whitelist()
def get_events(start, end, user=None, for_reminder=False, filters=None):

	if isinstance(filters, string_types):
		filters = json.loads(filters)

	events = frappe.db.sql("""select name, subject, description, color,
		starts_on, ends_on, owner, all_day, event_type, repeat_this_event, repeat_on,repeat_till,
		monday, tuesday, wednesday, thursday, friday, saturday, sunday, employee_emails
		from `tabvBooking Event` where ((
			(date(starts_on) between date(%(start)s) and date(%(end)s))
			or (date(ends_on) between date(%(start)s) and date(%(end)s))
			or (date(starts_on) <= date(%(start)s) and date(ends_on) >= date(%(end)s))
		) or (
			date(starts_on) <= date(%(start)s) and repeat_this_event=1 and
			ifnull(repeat_till, %(max_repeat_till)s) > date(%(start)s)
		))
		{reminder_condition}
		{filter_condition}
		order by starts_on""".format(
			filter_condition=get_filters_cond('Event', filters, []),
			reminder_condition="and ifnull(send_reminder,0)=1" if for_reminder else ""
		), {
			"max_repeat_till": max_repeat_till,
			"start": start,
			"end": end,
		}, as_dict=1)

	# process recurring events
	start = start.split(" ")[0]
	end = end.split(" ")[0]
	add_events = []
	remove_events = []

	def add_event(e, date):
		new_event = e.copy()

		enddate = add_days(date,int(date_diff(e.ends_on.split(" ")[0], e.starts_on.split(" ")[0]))) \
			if (e.starts_on and e.ends_on) else date
		new_event.starts_on = date + " " + e.starts_on.split(" ")[1]
		if e.ends_on:
			new_event.ends_on = enddate + " " + e.ends_on.split(" ")[1]
		add_events.append(new_event)

	for e in events:
		if e.repeat_this_event:
			e.starts_on = get_datetime_str(e.starts_on)
			if e.ends_on:
				e.ends_on = get_datetime_str(e.ends_on)

			event_start, time_str = get_datetime_str(e.starts_on).split(" ")
			if cstr(e.repeat_till) == "":
				repeat = max_repeat_till
			else:
				repeat = e.repeat_till
			if e.repeat_on=="Every Year":
				start_year = cint(start.split("-")[0])
				end_year = cint(end.split("-")[0])
				event_start = "-".join(event_start.split("-")[1:])

				# repeat for all years in period
				for year in range(start_year, end_year+1):
					date = str(year) + "-" + event_start
					if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) and getdate(date) <= getdate(repeat):
						add_event(e, date)

				remove_events.append(e)

			if e.repeat_on=="Every Month":
				date = start.split("-")[0] + "-" + start.split("-")[1] + "-" + event_start.split("-")[2]

				# last day of month issue, start from prev month!
				try:
					getdate(date)
				except ValueError:
					date = date.split("-")
					date = date[0] + "-" + str(cint(date[1]) - 1) + "-" + date[2]

				start_from = date
				for i in range(int(date_diff(end, start) / 30) + 3):
					if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) \
						and getdate(date) <= getdate(repeat) and getdate(date) >= getdate(event_start):
						add_event(e, date)
					date = add_months(start_from, i+1)

				remove_events.append(e)

			if e.repeat_on=="Every Week":
				weekday = getdate(event_start).weekday()
				# monday is 0
				start_weekday = getdate(start).weekday()

				# start from nearest weeday after last monday
				date = add_days(start, weekday - start_weekday)

				for cnt in range(int(date_diff(end, start) / 7) + 3):
					if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) \
						and getdate(date) <= getdate(repeat) and getdate(date) >= getdate(event_start):
						add_event(e, date)

					date = add_days(date, 7)

				remove_events.append(e)

			if e.repeat_on=="Every Day":
				for cnt in range(date_diff(end, start) + 1):
					date = add_days(start, cnt)
					if getdate(date) >= getdate(event_start) and getdate(date) <= getdate(end) \
						and getdate(date) <= getdate(repeat) and e[weekdays[getdate(date).weekday()]]:
						add_event(e, date)
				remove_events.append(e)

	for e in remove_events:
		events.remove(e)

	events = events + add_events

	for e in events:
		# remove weekday properties (to reduce message size)
		for w in weekdays:
			del e[w]

	return events
	