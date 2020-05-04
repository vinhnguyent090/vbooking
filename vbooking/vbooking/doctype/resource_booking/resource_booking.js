// Copyright (c) 2017, vinhnguyen.t090@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Resource Booking', {
	onload_post_render: function(frm) {
		frm.get_field("employees").grid.set_multiple_add("employee");
	},	
	onload: function(frm) {
		frm.set_query("ref_type", function(txt) {
			return {
				"filters": {
					"issingle": 0,
				}
			};
		});
	},
	refresh: function(frm) {
		if(frm.doc.ref_type && frm.doc.ref_name) {
			frm.add_custom_button(__(frm.doc.ref_name), function() {
				frappe.set_route("Form", frm.doc.ref_type, frm.doc.ref_name);
			});
		}
	},
	repeat_on: function(frm) {
		if(frm.doc.repeat_on==="Every Day") {
			["monday", "tuesday", "wednesday", "thursday",
				"friday", "saturday", "sunday"].map(function(v) {
					frm.set_value(v, 1);
				});
		}
	},
	vbooking_resource_check: function(frm) {
        // frm.set_value('color', '');
		if(cur_frm.doc.vbooking_resource_check=='1'){
			frm.set_value('event_type', "Public");
			var resource_name = cur_frm.doc.booking_resource;
			var booking = "Booking: ";
			if(resource_name){
				frm.set_value('subject', booking + resource_name);
				// frm.set_value('color', '#ff69b4');
			}
		}
    },
	booking_resource: function(frm) {
        // frm.set_value('color', '');
		if(cur_frm.doc.vbooking_resource_check=='1'){
            var resource_name = cur_frm.doc.booking_resource;
			// frm.set_value('color', '');
            if(resource_name){
				var booking = "Booking: ";
				// frm.set_value('color', '#ff69b4');
            	frm.set_value('subject', booking + resource_name);
			}
        } 
    },


});

cur_frm.add_fetch('booking_resource','color','color');