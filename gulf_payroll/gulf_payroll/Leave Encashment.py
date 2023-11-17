
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from frappe.utils import now
import json
from hrms.hr.doctype.leave_application.leave_application import get_leaves_for_period
from hrms.hr.doctype.leave_encashment.leave_encashment import LeaveEncashment
from hrms.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
	get_assigned_salary_structure,
)


class LeaveEncashment_new(Document):

	@frappe.whitelist()
	def get_leave_details_for_encashment(self):
		salary_structure = get_assigned_salary_structure(
			self.employee, self.encashment_date or getdate(nowdate())
		)
		if not salary_structure:
			frappe.throw(
				_("No Salary Structure assigned for Employee {0} on given date {1}").format(
					self.employee, self.encashment_date
				)
			)

		if not frappe.db.get_value("Leave Type", self.leave_type, "allow_encashment"):
			frappe.throw(_("Leave Type {0} is not encashable").format(self.leave_type))

		allocation = LeaveEncashment.get_leave_allocation(self)

		if not allocation:
			frappe.throw(
				_("No Leaves Allocated to Employee: {0} for Leave Type: {1}").format(
					self.employee, self.leave_type
				)
			)

		per_day_encashment = frappe.db.get_value(
			"Salary Structure", salary_structure, "leave_encashment_amount_per_day"
		)
		amount=int(per_day_encashment)
		amount1=json.dumps(amount)
		frappe.msgprint("amount per day:"+ amount1)
		joining_date=frappe.db.get_value(
			"Employee",self.employee, "date_of_joining"
		)
		joining_date_str = str(joining_date)
		joining_date1 = json.dumps(joining_date_str)
		frappe.msgprint("joing date:" +joining_date1)
		current_time = getdate(now())
		curnt_dte = str(current_time)
		new=json.dumps(curnt_dte)
		frappe.msgprint("current date:"+new)
		total_years = (current_time-joining_date).days // 365
		tot=int(total_years)
		years=json.dumps(tot)
		frappe.msgprint("total years worked:"+years)
		var= get_leaves_for_period(
				self.employee, self.leave_type, allocation.from_date, self.encashment_date
			)
		var1=int(var)
		var2=json.dumps(var1)
		frappe.msgprint("total leave taken:" + var2)
		
		if total_years < 5:
			self.leave_balance = (
			21 - allocation.carry_forwarded_leaves_count
			
			+ get_leaves_for_period(
				self.employee, self.leave_type, allocation.from_date, self.encashment_date
			)
		)
			self.encashment_amount = (
			self.leave_balance *  per_day_encashment if per_day_encashment > 0 else 0
		)
			total_amount=self.encashment_amount
			total=int(total_amount)
			total1=json.dumps(total)
			frappe.msgprint("total_amount:"+total1)
		else:
			self.leave_balance = (
			28 - allocation.carry_forwarded_leaves_count
			
			+ get_leaves_for_period(
				self.employee, self.leave_type, allocation.from_date, self.encashment_date
			)
		)
			self.encashment_amount = (
			self.leave_balance *  per_day_encashment if per_day_encashment > 0 else 0
		)
			total_amount=self.encashment_amount
			total=int(total_amount)
			total1=json.dumps(total)
			frappe.msgprint("total_amount:"+total1)
   
		encashable_days = self.leave_balance - frappe.db.get_value(
			"Leave Type", self.leave_type, "encashment_threshold_days"
		)
		self.encashable_days = encashable_days if encashable_days > 0 else 0

		
		self.leave_allocation = allocation.name
		return True

	