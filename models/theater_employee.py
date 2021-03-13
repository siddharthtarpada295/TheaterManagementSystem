from odoo import api, fields, models
from datetime import datetime
from dateutil import relativedelta
from odoo.exceptions import ValidationError
import re

class TheaterEmployee(models.Model):
	_name = "theater.employee"
	_description = "Theater Employee"

	name = fields.Char(string="Name", required=True)
	birthdate = fields.Date(string="Birthdate", required=True)
	age = fields.Char()
	gender = fields.Selection([
		('male','Male'),
		('female','Female'),
		('other','Other')], required=True)
	mobile = fields.Char(string="Mobile", required=True)
	email = fields.Char(string="Email")
	city = fields.Char(string="City")
	state_id = fields.Many2one('res.country.state', string="State")
	country_id = fields.Many2one('res.country', string="Country")
	joiningdate = fields.Date(string="Joining Date", required=True)
	experience = fields.Char(string="Experience", compute="compute_experience")
		

	@api.onchange('birthdate')
	def get_age(self):
		if self.birthdate:
			dob = datetime.strptime(str(self.birthdate), "%Y-%m-%d")
			computed_age = int((datetime.today() - dob).days/365)
			if (computed_age) < 18:
				raise ValidationError("Age Restriction For Employee below 18.")
			else:
				self.age = (str((computed_age)) + " Years")

	@api.onchange('state_id')
	def _on_change_state_id(self):
		print("ON CHANGE CALLED")
		self.country_id = False
		self.country_id = self.state_id.country_id and self.state_id.country_id.id or False

	@api.onchange('mobile')
	def _on_change_mobile(self):
		if self.mobile:
			if re.match("^[0-9]{10}$", self.mobile) == None:
				raise ValidationError("Enter valid 10 digits Mobile number.")

	@api.onchange('email')
	def _on_change_email(self):
		if self.email:
			if re.match('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', self.email) == None:
				raise ValidationError("Enter valid Email address.")

	@api.depends('joiningdate')
	def compute_experience(self):
		for theater in self:
			theater.experience = False
			if theater.joiningdate:
				now = datetime.today().date()
				experience = relativedelta.relativedelta(now, theater.joiningdate)
				theater.experience = (str(experience.years) + " Years, " \
					+ str(experience.months) + " Months, " + str(experience.days) + " Days")
			
