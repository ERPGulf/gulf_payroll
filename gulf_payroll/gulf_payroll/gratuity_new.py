# # Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt


from math import floor
import json
import frappe
from frappe import _, bold
from frappe.query_builder.functions import Sum
from frappe.utils import flt, get_datetime, get_link_to_form
from hrms.payroll.doctype.gratuity.gratuity import get_gratuity_rule_slabs
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
# #  "erpnext.controllers.taxes_and_totals.calculate_taxes_and_totals": "test_app.override.Calculating_amount"
from hrms.payroll.doctype.gratuity.gratuity import Gratuity
from hrms.payroll.doctype.gratuity.gratuity import calculate_work_experience
from frappe.model.document import Document
class Gratuity_new(AccountsController):
    def validate(self):
        data = calculate_work_experience_and_amount(self.employee, self.gratuity_rule)
        self.current_work_experience = data["current_work_experience"]
        self.amount = data["amount"]
        self.set_status()
 
@frappe.whitelist()
def calculate_work_experience_and_amount(employee, gratuity_rule):
	current_work_experience =calculate_work_experience(employee, gratuity_rule) or 0
	gratuity_amount =calculate_gratuity_amount(employee, current_work_experience) or 0

	return {"current_work_experience": current_work_experience, "amount": gratuity_amount}

def calculate_gratuity_amount(employee, experience):
        frappe.msgprint("inside calculate")
        gratuity_amount = 0
        year_left = experience
        gratuity_amount =calculate_amount_based_on_current_slab(experience,employee)
                
        return gratuity_amount


def calculate_amount_based_on_current_slab(experience,employee):
       
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
        data=int(current_salary)
        one_day1=json.dumps(data)
        frappe.msgprint("monthly salary:" +one_day1)
        one_day= data / 30
        one_day2=json.dumps(one_day)
        frappe.msgprint("one day salary:" +one_day2)
        if experience >= 5:
        #  if experience >= from_year and (to_year == 0 or experience < to_year):
            gratuity_amount = (
            28* experience * one_day
            )
        else:
            gratuity_amount = (
            21* experience * one_day
            )
            # gratuity_amount = (
            # 	total_applicable_components_amount * experience * fraction_of_applicable_earnings
            # )
            

        return  gratuity_amount

