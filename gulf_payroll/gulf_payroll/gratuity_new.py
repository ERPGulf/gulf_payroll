# # Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt


from math import floor
import json
import frappe
from frappe.utils import getdate, nowdate
from frappe.utils import now
from frappe import _, bold
from frappe.query_builder.functions import Sum
from frappe.utils import flt, get_datetime, get_link_to_form
from hrms.payroll.doctype.gratuity.gratuity import get_gratuity_rule_slabs
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from hrms.payroll.doctype.gratuity.gratuity import Gratuity
from hrms.payroll.doctype.gratuity.gratuity import calculate_work_experience
from hrms.hr.doctype.leave_application.leave_application import get_leaves_for_period
from hrms.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
	get_assigned_salary_structure,
)
from frappe.model.document import Document
class Gratuity_new(AccountsController):
    def validate(self):
        data = calculate_work_experience_and_amount(self.employee, self.gratuity_rule)
        self.custom_work_experience = data["current_work_experience"]
        self.amount = data["amount"]
        self.set_status()
        
        
    def on_submit(self):
        if self.pay_via_salary_slip:
            Gratuity.create_additional_salary(self)
        else:
            Gratuity.create_gl_entries()
 
@frappe.whitelist()
def calculate_work_experience_and_amount(employee, gratuity_rule):
    date=frappe.db.get_value(
			"Employee",employee, "date_of_joining"
		)
    relieving_date=frappe.db.get_value(
			"Employee",employee, "relieving_date"
		)
    if not relieving_date :
            frappe.throw(
			_("Please set relieving date for employee: {0}").format(
				bold(get_link_to_form("Employee", employee))
			)
		)
    delta = relieving_date - date
    total_days = delta.days

		# Calculate the number of years as a floating-point value
    total_years = total_days / 365
    total_years1=round(total_years, 9)
    current_work_experience =total_years
    gratuity_amount =calculate_gratuity_amount(employee, current_work_experience) or 0

    return {"current_work_experience": current_work_experience, "amount": gratuity_amount}

def calculate_gratuity_amount(employee,experience):
       
        gratuity_amount = 0
        year_left = experience
        gratuity_amount =calculate_amount_based_on_current_slab(experience,employee)
        return gratuity_amount


def calculate_amount_based_on_current_slab(self,employee):
       
        gratuity_amount = 0
        current_salary=frappe.db.get_value(
            "Employee", employee,"custom_current_basic_salary"
        )
        if not current_salary:
            frappe.throw(
			_("Please set current salary for employee: {0}").format(
				bold(get_link_to_form("Employee", employee))
			)
		)
        date=frappe.db.get_value(
			"Employee",employee, "date_of_joining"
		)
        relieving_date=frappe.db.get_value(
			"Employee",employee, "relieving_date"
		)
        data=int(current_salary)
        one_day1=json.dumps(data)
        frappe.msgprint("monthly salary:" +one_day1)
        one_day= data / 30
        one_day2=json.dumps(one_day)
        frappe.msgprint("one day salary:" +one_day2)
        relieving_dte = str(relieving_date)
        new = json.dumps(relieving_dte)
        frappe.msgprint("relieving date:"+new)
        delta = relieving_date - date
        total_days = delta.days

		# Calculate the number of years as a floating-point value
        total_years = total_days / 365
        total_years1=round(total_years, 9)
        total=json.dumps(total_years1)
		# Display the total years with two decimal places
        frappe.msgprint("work experience:"+total)
        deduct = frappe.get_doc('Leave Encashment setting').get('deduct_leave_days_from_gratuity')
        if total_years1<1:
            frappe.throw("gratuity only applicable to above one year experience")
        if total_years1 >= 5:
            Allocated_leaves_1 = frappe.get_doc('Leave Encashment setting').get('allocated_dayss') 
            allocated_int1=int(Allocated_leaves_1)
            allocated1=json.dumps(allocated_int1)
            frappe.msgprint("Allocated leaves:"+allocated1)
            if deduct:
                
                doc = frappe.db.get_list(
                'Attendance',
                fields=['status'],
                filters={'status':'On Leave','employee':employee, 'docstatus': 1},
                )
                total_leaves = len(doc)
                total_leaves1=int(total_leaves)
                total_leaves2=json.dumps(total_leaves1)
                frappe.msgprint("total leaves:"+total_leaves2)

                year=total_years*365
                alocate_total=total_years*allocated_int1
                salary_structure = get_assigned_salary_structure(
			    employee, relieving_date or getdate(nowdate())
		        )
                per_day_encashment = frappe.db.get_value(
			    "Salary Structure", salary_structure, "leave_encashment_amount_per_day"
		        )
                leave_type11=str(per_day_encashment)
                leave_type21=json.dumps(leave_type11)
                frappe.msgprint("per day:"+leave_type21)
                gratuity_amount= (
			    (alocate_total/year)*(year-(total_leaves))*one_day
		        )
            else:
                gratuity_amount = (
                allocated_int1 * total_years1 * one_day
                
                 )

            
        else:
            Allocated_leaves = frappe.get_doc('Leave Encashment setting').get('allocated_days') 
            allocated_int=int(Allocated_leaves)
            allocated=json.dumps(allocated_int)
            frappe.msgprint("Allocated leaves:"+allocated)

            gratuity_amount = (
            allocated_int *total_years1* one_day
            )
            if deduct:
                
                doc = frappe.db.get_list(
                'Attendance',
                fields=['status'],
                filters={'status':'On Leave','employee':employee, 'docstatus': 1},
                )
                total_leaves = len(doc)
                total_leaves1=int(total_leaves)
                total_leaves2=json.dumps(total_leaves1)
                frappe.msgprint("total leaves:"+total_leaves2)

                year=total_years*365
                alocate_total=total_years*allocated_int
                salary_structure = get_assigned_salary_structure(
			    employee, relieving_date or getdate(nowdate())
		        )
                per_day_encashment = frappe.db.get_value(
			    "Salary Structure", salary_structure, "leave_encashment_amount_per_day"
		        )
                leave_type11=str(per_day_encashment)
                leave_type21=json.dumps(leave_type11)
                frappe.msgprint("per day:"+leave_type21)
                gratuity_amount= (
			    (alocate_total/year)*(year-(total_leaves))*one_day
		        )
       
            
        return  gratuity_amount

