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

class TagsCategories(models.Model):
	_name = 'tags.categories'
	_description = 'Theater Shows Tags'

	name  = fields.Char(string='Name', required=True)
	color = fields.Integer(string='Color', required=True)
	# tag_ids = fields.Many2many('theater.show')
	sequence = fields.Integer(string="Sequence", default="1")

	@api.constrains('name')
	def _tags_constrains(self):
		tags = []
		# records = self.read(['id'])
		records1 = self.read_group([('id', 'not in', [self.id])], \
			['name'],['name'])
		for record in records1:
			tags.append(record['name'].lower())
		for record in self:
			if record.name.lower() in tags:
				raise ValidationError("Tag name Must be unique in tags.")

	# @api.model_create_multi
	# def create(self, vals):
	#     print("CALLING CREATE METHOD : ", vals)
	#     res = super(TagsCategories, self).create(vals)
	#     print("NEW CREATED RECORD'S id: ", res.id)
	#     return res

	# def write(self, vals):
	#     print("CALLING WRITE METHOD : ", self.id,vals)
	#     res = super(TagsCategories, self).write(vals)
	#     print("CURRENT RECORD's id: ", self.id)
	#     return res

class ConfigurationStages(models.Model):
	_name = 'configuration.stages'
	_description = 'Configuration Stages'
	_order = 'sequence asc'

	name = fields.Char(string='Name', required=True)
	stage_active = fields.Selection([
		('days_before','Days Before'),
		('days_between','Days Between'),
		('days_after','Days After')], string='Active Stage', default='days_between')
	days = fields.Integer(default=0)
	sequence = fields.Integer(string="Sequence", default="1")

	@api.constrains('name')
	def _stages_constrains(self):
		stages = []
		# records = self.read(['id'])
		records1 = self.read_group([('id', 'not in', [self.id])], \
			['name'],['name'])
		for record in records1:
			stages.append(record['name'].lower())
		for record in self:
			if record.name.lower() in stages:
				raise ValidationError("Stage name Must be unique in stages.")

	@api.constrains('stage_active')
	def _stage_active_constrains(self):
		if self.stage_active != 'days_before':
			count = self.search_count([('stage_active', '=', self.stage_active)])
			if count > 1:
				raise ValidationError("Please Change the active stage because chosen active stage is use only single time.")

class MovieCast(models.Model):
	_name = "movie.cast"
	_description = "Detail Profile About Actor and Actress"

	name = fields.Char(string="Name", required=True)
	image = fields.Binary()
	dob = fields.Date(string="Birth Date", required=True)
	date_begin = fields.Date(required=True)
	date_end = fields.Date(required=True)
	city = fields.Char(string="City")
	state_id = fields.Many2one('res.country.state', string="State")
	country_id = fields.Many2one('res.country', string="Country")
	occupation = fields.Selection([
		('actor','Actor'),
		('actress','Actress')])
	movie_id = fields.Many2many('theater.movie','cast_ids')

	@api.onchange('state_id')
	def _on_change_state_id(self):
		print("ON CHANGE CALLED")
		self.country_id = False
		self.country_id = self.state_id.country_id and self.state_id.country_id.id or False

class TheaterScreens(models.Model):
	_name = "theater.screens"
	_description = "Screens of Theater"
	_rec_name = 'name'

	name = fields.Char(string="Name", required=True, copy=False)
	seats_capacity = fields.Integer(string="Capacity")

	time_id = fields.One2many("show.timing","screen_id",string='Show Timings')

class ShowTiming(models.Model):
	_name = "show.timing"
	_description = "Show Timing For Perticular Screen"

	screen_id = fields.Many2one("theater.screens")

	time_begin = fields.Char(string='Start Time')
	time_end = fields.Char(string="End Time")

	def name_get(self):
		return [(time.id, "%s - %s" % (time.time_begin,time.time_end)) for time in self]

class Shows(models.Model):
	_name = 'shows'
	_description = "Day to day Shows per Screens"

	show_id = fields.Many2one('theater.shows')
	date = fields.Date(string="Date")
	venue_id = fields.Many2one("theater.screens")
	time_id = fields.Many2one('show.timing', domain="[('screen_id','=',venue_id)]")

class ScreenSeating(models.Model):
	_name = "screen.seating"
	_description = "Screen Seating"

	name = fields.Char(string="Name")
	capacity = fields.Integer(string="Capacity")


	





