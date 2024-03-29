# -*- coding: utf-8 -*-
# Copyright (c) 2019, PT. UNITEK MAS INDONESIA and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
from frappe.utils import get_fullname, now
from frappe.model.document import Document
from frappe.core.utils import get_parent_doc, set_timeline_doc
import frappe

class ActivityLog(Document):
	def before_insert(self):
		self.full_name = get_fullname(self.user)
		self.date = now()

	def validate(self):
		self.set_status()
		set_timeline_doc(self)

	def set_status(self):
		if not self.is_new():
			return

		if self.reference_doctype and self.reference_name:
			self.status = "Linked"

	def on_trash(self): # pylint: disable=no-self-use
		frappe.throw(_("Sorry! You cannot delete auto-generated comments"))

def on_doctype_update():
	"""Add indexes in `tabActivity Log`"""
	frappe.db.add_index("Activity Log", ["reference_doctype", "reference_name"])
	frappe.db.add_index("Activity Log", ["timeline_doctype", "timeline_name"])
	frappe.db.add_index("Activity Log", ["link_doctype", "link_name"])

def add_authentication_log(subject, user, operation="Login", status="Success"):
	frappe.get_doc({
		"doctype": "Activity Log",
		"user": user,
		"status": status,
		"subject": subject,
		"operation": operation,
	}).insert(ignore_permissions=True, ignore_links=True)

def clear_authentication_logs():
	"""clear 100 day old authentication logs"""
	frappe.db.sql("""delete from `tabActivity Log` where \
	creation<DATE_SUB(NOW(), INTERVAL 100 DAY)""")