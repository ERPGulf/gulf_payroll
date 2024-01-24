
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from frappe.utils import now
import json
from hrms.hr.doctype.leave_application.leave_application import get_leaves_for_period
from hrms.hr.doctype.leave_encashment.leave_encashment import LeaveEncashment
# from hrms.hr.doctype.leave_encashment.leave_encashment import get_leave_allocation
from hrms.hr.utils import set_employee_name, validate_active_employee
from frappe.utils import add_days, date_diff, flt, formatdate, get_link_to_form, getdate
from hrms.hr.doctype.leave_ledger_entry.leave_ledger_entry import create_leave_ledger_entry
from hrms.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
	get_assigned_salary_structure,
)
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

class OverlapError(frappe.ValidationError):
	pass
class LeaveEncashment_new(Document):
	def validate(self):
		set_employee_name(self)
		validate_active_employee(self.employee)
		self.get_leave_details_for_encashment()
		LeaveEncashment.validate_salary_structure(self)
		self.submited_leave_encashment()
		self.validate_period()
		
  
		if not self.encashment_date:
			self.encashment_date = getdate(nowdate())
   
	def validate_period(self):
		if date_diff(self.custom_to_date, self.custom_from_date) <= 0:
			frappe.throw(_("To date cannot be before from date"))

	@frappe.whitelist()
	def submited_leave_encashment(self):
		doc = frappe.db.sql(
    """
    SELECT name 
    FROM `tabAttendance`
    WHERE 
        (attendance_date BETWEEN %s AND %s) AND 
        (attendance_date BETWEEN %s AND %s) AND
        employee= %s AND docstatus=1
    """,
    	(self.custom_from_date,self.custom_to_date,self.custom_from_date,self.custom_to_date,self.employee,)
)
		if len(doc)==0:
					
			frappe.msgprint(("No Leaves Allocated to Employee: {0} for Leave  period: {1} to {2}").format(
					self.employee, self.custom_from_date,self.custom_to_date
				)
			)
					
 
	def on_submit(self):
		if not self.leave_allocation:
			self.leave_allocation = self.get_leave_allocation().get("name")
		additional_salary = frappe.new_doc("Additional Salary")
		additional_salary.company = frappe.get_value("Employee", self.employee, "company")
		additional_salary.employee = self.employee
		additional_salary.currency = self.currency
		earning_component = frappe.get_value("Leave Type", self.leave_type, "earning_component")
		if not earning_component:
			frappe.throw(_("Please set Earning Component for Leave type: {0}.").format(self.leave_type))
		additional_salary.salary_component = earning_component
		additional_salary.payroll_date = self.encashment_date
		additional_salary.amount = self.encashment_amount
		additional_salary.ref_doctype = self.doctype
		additional_salary.ref_docname = self.name
		additional_salary.submit()

		# Set encashed leaves in Allocation
		frappe.db.set_value(
			"Leave Allocation",
			self.leave_allocation,
			"total_leaves_encashed",
			frappe.db.get_value("Leave Allocation", self.leave_allocation, "total_leaves_encashed")
			+ self.encashable_days,
		)

		LeaveEncashment.create_leave_ledger_entry(self)

	def on_cancel(self):
		if self.additional_salary:
			frappe.get_doc("Additional Salary", self.additional_salary).cancel()
			self.db_set("additional_salary", "")

		if self.leave_allocation:
			frappe.db.set_value(
				"Leave Allocation",
				self.leave_allocation,
				"total_leaves_encashed",
				frappe.db.get_value("Leave Allocation", self.leave_allocation, "total_leaves_encashed")
				- self.encashable_days,
			)
		LeaveEncashment.create_leave_ledger_entry(self,submit=False)
	def get_leave_allocation(self):
		date = self.encashment_date or getdate()

		LeaveAllocation = frappe.qb.DocType("Leave Allocation")
		leave_allocation = (
			frappe.qb.from_(LeaveAllocation)
			.select(
				LeaveAllocation.name,
				LeaveAllocation.from_date,
				LeaveAllocation.to_date,
				LeaveAllocation.carry_forwarded_leaves_count,
			)
			.where(
				((LeaveAllocation.from_date <= date) & (date <= LeaveAllocation.to_date))
				& (LeaveAllocation.docstatus == 1)
				& (LeaveAllocation.leave_type == self.leave_type)
				& (LeaveAllocation.employee == self.employee)
	
			)
		).run(as_dict=True)

		return leave_allocation[0] if leave_allocation else None
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

		allocation = self.get_leave_allocation()

		if not allocation:
			frappe.throw(
				_("No Leaves Allocated to Employee: {0} for Leave Type: {1}").format(
					self.employee, self.leave_type
				)
			)
		previous_leave_encashment = frappe.get_list(
			'Leave Encashment',
            fields=['custom_to_date','custom_from_date'],
			filters={
				'employee':self.employee,
				'docstatus': 1,
			},
			order_by='custom_to_date DESC',
   
			limit=1
		)
		frappe.msgprint(f"previous leave encashment: {previous_leave_encashment}")
		previous_leave_encashment_name = frappe.get_list(
			'Leave Encashment',
            fields=['name'],
			filters={
				'employee':self.employee,
				'docstatus': 1,
				'leave_type':self.leave_type
			},
			order_by='custom_to_date DESC',
   
			limit=1
		)
		frappe.msgprint(f"previous leave encashment: {previous_leave_encashment_name}")
		
		doc = frappe.db.sql(
    """
    SELECT name 
    FROM `tabLeave Encashment`
    WHERE 
        
        (custom_to_date BETWEEN %s AND %s) AND
        employee= %s AND docstatus=1
    """,
    	(self.custom_from_date,self.custom_to_date,self.employee,)
		)
		if len(previous_leave_encashment) > 0:
			frappe.msgprint(str(len(previous_leave_encashment)))
			

			previous_custom_from_date = previous_leave_encashment[0].get("custom_from_date")
			previous_custom_to_date = previous_leave_encashment[0].get("custom_to_date")
			if not previous_custom_from_date and not previous_custom_to_date:
				frappe.msgprint("no leave encashment")
				date = self.custom_from_date
				frappe.msgprint(f"From Date: {date}")
				self.custom_to_date = add_days(date, 365)
				frappe.msgprint(f"To Date: {self.custom_to_date}")

		
			else:
				frappe.msgprint("already leaves allocated")
				previous_custom_to_date = previous_leave_encashment[0].get("custom_to_date")
				if not self.custom_from_date:
					self.custom_from_date = add_days(previous_custom_to_date, 1)

				# If custom_to_date is not set, default to one year from custom_from_date
				if not self.custom_to_date:
					self.custom_to_date = add_days(self.custom_from_date, 365)
					curent_to_date=self.custom_to_date
					date_to=str(curent_to_date)
				if date_diff(self.custom_to_date,previous_custom_to_date) <= 0:
					name=previous_leave_encashment_name[0].get("name")
					
					frappe.throw(
					_("Unable to make a submission as the period from {0} to {1} comes before the date when the leave encashment was previously submitted. Reference:{2}. ").format(
						self.custom_from_date, self.custom_to_date,name
					)
				)
				
				to_date = self.custom_to_date
				frappe.msgprint(f"To Date: {to_date}")
				from_date = self.custom_from_date
				frappe.msgprint(f"From Date: {from_date}")
		
			# If no previous leave encashment record, use existing custom_from_date
		
		per_day_encashment = frappe.db.get_value(
			"Salary Structure", salary_structure, "leave_encashment_amount_per_day"
		)
		amount=int(per_day_encashment)
		amount1=json.dumps(amount)
		
		frappe.msgprint("amount per day:"+ amount1)
		# frappe.msgprint(per_day_encashment)
		date = self.custom_from_date
		frappe.msgprint(f"From Date: {date}")
		if not self.custom_to_date:
			self.custom_to_date = add_days(date, 365)
		date=frappe.db.get_value(
			"Employee",self.employee, "date_of_joining"
		)

		joining_date_str = str(date)
		joining_date = json.dumps(joining_date_str)
		frappe.msgprint("joing date:" +joining_date)
		current_time = getdate(now())
		curnt_dte = str(current_time)
		new = json.dumps(curnt_dte)
		frappe.msgprint("current date:"+new)
		delta = current_time - date
		total_days = delta.days
		# Calculate the number of years as a floating-point value
		total_years = total_days / 365.25

		# Display the total years with two decimal places
		frappe.msgprint(f"Total years worked: {total_years:.1f}")

		var= get_leaves_for_period(
				self.employee, self.leave_type, allocation.from_date, self.encashment_date
			)
		total_leaves_doc = frappe.db.sql(
		"""
		SELECT name 
		FROM `tabAttendance`
		WHERE 
			(attendance_date BETWEEN %s AND %s) AND
			employee = %s AND docstatus = 1
		""",
    	(self.custom_from_date, self.custom_to_date, self.employee,)
		)

		total_leaves = len(total_leaves_doc)
		var1=int(total_leaves)
		var2=json.dumps(var1)
		frappe.msgprint(f"total leavess: {total_leaves}")
		leave_type = frappe.db.sql(
		"""
		SELECT name 
		FROM `tabAttendance`
		WHERE 
			(attendance_date BETWEEN %s AND %s) AND leave_type=%s AND
			employee = %s AND docstatus = 1
		""",
    	(self.custom_from_date, self.custom_to_date,self.leave_type,self.employee,)
		)
		base_amount=frappe.db.get_list("Salary Structure Assignment",fields=["base"],filters={'salary_structure': ['like', f'{salary_structure}'],'docstatus':['like',1]})
		for base_amount1 in base_amount:
			base=base_amount1.get("base")
			base1 = int(base)
			base2 = json.dumps(base1)	
			frappe.msgprint(base2)
		
		one_day= base1 / 30
		one_day2=json.dumps(one_day)
		frappe.msgprint("one day salaryy:" +one_day2)
                  
		
		leave_type_leaves=len(leave_type)
		frappe.msgprint(f"leave type leaves: {leave_type_leaves}")
		basic_salary = frappe.get_doc('Leave Encashment setting').get('basic_salary_per_day')
		if total_years<1:
			frappe.throw("Leave encashment only applicable to above one year experience")
		elif 1 <= total_years <= 5:
			Allocated_leaves = frappe.get_doc('Leave Encashment setting').get('allocated_days') 
			allocated_int=int(Allocated_leaves)
			allocated=json.dumps(allocated_int)
			frappe.msgprint("Allocated leaves:"+allocated)
			self.leave_balance=(allocated_int-leave_type_leaves)
			year=365
			encashable_days= (
			(allocated_int/year)*(year-(total_leaves))
		)
			self.encashable_days = encashable_days if encashable_days > 0 else 0
			if basic_salary:
				self.encashment_amount = (
				(allocated_int/year)*(year-(total_leaves))*one_day)
				total_amount=self.encashment_amount
				total=int(total_amount)
				total1=json.dumps(total)
				frappe.msgprint("total_amount:"+total1)
			else:
				self.encashment_amount = (
				(allocated_int/year)*(year-(total_leaves))*per_day_encashment)
				total_amount=self.encashment_amount
				total=int(total_amount)
				total1=json.dumps(total)
				frappe.msgprint("total_amount:"+total1)
			
		else:
			Allocated_leaves_1 = frappe.get_doc('Leave Encashment setting').get('allocated_dayss') 
			allocated_int=int(Allocated_leaves_1)
			allocated1=json.dumps(allocated_int)
			frappe.msgprint("Allocated leaves:"+allocated1)
	
			self.leave_balance=(allocated_int-leave_type_leaves)
			
			year=365
		encashable_days= (
			(allocated_int/year)*(year-(total_leaves))
		)
		self.encashable_days = encashable_days if encashable_days > 0 else 0
		if basic_salary:
				self.encashment_amount = (
				(allocated_int/year)*(year-(total_leaves))*one_day)
				total_amount=self.encashment_amount
				total=int(total_amount)
				total1=json.dumps(total)
				frappe.msgprint("total_amount:"+total1)
		else:
				self.encashment_amount = (
				(allocated_int/year)*(year-(total_leaves))*per_day_encashment)
				total_amount=self.encashment_amount
				total=int(total_amount)
				total1=json.dumps(total)
				frappe.msgprint("total_amount:"+total1)
		self.leave_allocation = allocation.name
		return True
	

	