from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from werkzeug.urls import url_encode

class TheaterBooking(models.Model):
	_name = "theater.booking"
	_inherit = "mail.thread"
	_description = "Theater Booking"

	name = fields.Many2one("res.partner", required=True, string="Name", tracking=1)
	email = fields.Char(related="name.email", string="Email")
	mobile = fields.Char(related="name.phone", string="Mobile")
	city = fields.Char(related="name.city", string="City")
	state_id = fields.Many2one(related="name.state_id", string="State")
	country_id = fields.Many2one(related="name.country_id", string="Country")

	show_id = fields.Many2one("theater.show", string="Show Title", required=True, tracking=0, domain="[('date_end', '>=', bookingdate)]")
	venue_id = fields.Many2one("theater.screens")
	seats_capacity = fields.Integer(related="venue_id.seats_capacity")
	time_id = fields.Many2one('show.timing', domain="[('screen_id','=',venue_id)]")

	date_end = fields.Date(related="show_id.date_end")
	ticket_id = fields.One2many(related="show_id.ticket_id")
	seats_max = fields.Integer(related="show_id.seats_max")
	currency_id = fields.Many2one(related="show_id.currency_id")
	price = fields.Monetary(related="show_id.price", string='Price')
	bookingcounter = fields.Integer(compute='seats_count', store=True)

	# employee_id = fields.Many2one("theater.employee", string="Booked by", required=True, tracking=3)
	employee_id = fields.Many2one("hr.employee", required=True, string="Booked by")
	product_type = fields.Many2one('product.product', required=True, string="Product Type")
	
	seats_qty = fields.Integer(string='Seats', default=0, required=True)
	untaxed_amount = fields.Monetary(string="Untaxed Amount ", compute='compute_price', store=True)
	taxed_amount = fields.Monetary(string="Total ", compute='compute_price', store=True)
	tax = fields.Monetary(string="Tax 20% ", compute='compute_price', store=True)
	discount = fields.Integer(string="Discount", default=0)
	discount_amount = fields.Monetary(compute='compute_price', store=True)

	bookingdate = fields.Date(string="Booking Date", default=datetime.today())
	watchingdate = fields.Date(string="Show Date")
	state = fields.Selection([
		('draft','Unconfirmed'),
		('open','Confirmed'),
		('done','Attended'),
		('cancel','Cancelled')], default='draft', string="Booking State", tracking=2)
	invoice_count = fields.Integer(string='Invoice Count', readonly=True, compute="compute_invoices")
	invoice_ids = fields.Many2many("account.move", string='Invoices', readonly=True, copy=False)
	# invoice_ids = fields.Integer(string='Invoices', readonly=True, copy=False)


	# _sql_constraints = [('watchingdate_check','CHECK(watchingdate < date_end)','Please Select the proper date.')]
	@api.constrains('watchingdate')
	def check_watchindate(self):
		if self.show_id:
			if self.watchingdate > self.date_end:
				raise ValidationError("Please Select Date between %s to %s." \
				 % (self.bookingdate,self.date_end))

	def action_confirm(self):
		for rec in self:
			rec.write({'state':'open'})

	def action_set_done(self):
		for rec in self:
			rec.write({'state':'done'})


	def action_set_draft(self):
		for rec in self:
			rec.write({'state':'draft'})

	def action_cancel(self):
		for rec in self:
			rec.write({'state':'cancel'})

	@api.depends('seats_qty', 'discount', 'show_id')
	def compute_price(self):
		for rec in self:
			if rec.seats_qty:
				rec.untaxed_amount = rec.price * rec.seats_qty
				rec.tax = (rec.untaxed_amount * 20) / 100
				rec.discount_amount = ((rec.untaxed_amount + rec.tax) * rec.discount) / 100
				rec.taxed_amount = rec.untaxed_amount + rec.tax - rec.discount_amount

	@api.onchange('seats_qty','show_id','venue_id')
	def seats_count(self):
		print("SHOW ID",self.show_id)
		if self.show_id:
			if self.venue_id:
				print("SEATS COUNT CALLED")
				count = sum(self.search([('show_id.id','=',self.show_id.id),
					('venue_id','=',self.venue_id.id),
					('time_id','=',self.time_id.id),
					('watchingdate','=',self.watchingdate)]).mapped('seats_qty'))
				if self.seats_max != -1:
					seats_left = self.seats_max - count
					print("SEATS LEFT",seats_left)
				else:
					seats_left = self.seats_capacity - count
					print(self.seats_capacity)
					print(count)
					print("SEATS LEFT 2 : ",seats_left)
				if seats_left < self.seats_qty:
						raise ValidationError('No More than %s seats available on this Show.' % seats_left)


	def create_invoices(self):
		if not self.env['account.move'].check_access_rights('create', False):
			try:
				self.check_access_rights('write')
				self.check_access_rule('write')
			except AccessError:
				return self.env['account.move']

		print("CREATE INVOISE CALLED")
		print("PARTENER ID : ",self.name.id)
		invoice_vals_list = {
			'partner_id': self.name.id,
			'move_type':'out_invoice',
			'state': 'draft',
			'invoice_date': self.bookingdate,
			'invoice_payment_term_id': 1,
			'invoice_line_ids': [{
				'product_id':self.product_type.id,
				'name': self.show_id.movie_id.name,
				'account_id': 2,
				'analytic_account_id': 1,
				'quantity': self.seats_qty,
				'tax_ids':[3],
				'discount':self.discount,
				'price_unit': self.price,

			}]
		}
		moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
		self.invoice_ids = [(4,moves.id,moves)]
		return moves

	def action_view_invoice(self):
		invoices = self.invoice_ids
		action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
		print("LENGTH OF INVOICE : ",invoices)
		if len(invoices) > 1:
			action['domain'] = [('id', 'in', invoices.ids)]
		elif len(invoices) == 1:
			form_view = [(self.env.ref('account.view_move_form').id, 'form')]
			if 'views' in action:
				action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
			else:
				action['views'] = form_view
			action['res_id'] = invoices.id
		else:
			action = {'type': 'ir.actions.act_window_close'}

		context = {
			'default_move_type': 'out_invoice',
		}
		action['context'] = context
		return action

	@api.depends('invoice_ids')
	def compute_invoices(self):
		invoice_ids = self.env["account.move"].search([])
		for rec in self.invoice_ids:
			flag = 0
			for rec1 in invoice_ids:
				if rec1 == rec:
					flag = 1
			if flag == 0:
				rec = ([2,rec.id,_])

		for rec in self:
			rec.invoice_count = len(rec.invoice_ids)


