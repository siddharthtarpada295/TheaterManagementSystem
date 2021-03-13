from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

class TheaterShows(models.Model):
    _name = "theater.show"
    _inherit = "mail.thread"
    _description = "Theater Show"
    _rec_name = "movie_id"

    movie_id = fields.Many2one('theater.movie', string='Show Title', required=True, tracking=True)
    minutes = fields.Integer(related="movie_id.minutes", string='Total Minutes')
    hours = fields.Float(related="movie_id.hours", string='Duration')
    director = fields.Char(related="movie_id.director", string='Director')
    tag_ids = fields.Many2many(related="movie_id.tag_ids", string="Tags")
    image = fields.Binary(related="movie_id.image")
    language_id = fields.Many2one(related="movie_id.language_id", string="Language")
    
    currency_id = fields.Many2one("res.currency", string='Currency')
    price = fields.Monetary(string='Price', tracking=True)
    # date = fields.Date(string='Date', tracking=True, copy=False, required=True)
    date_begin = fields.Date(required=True, tracking=True, copy=False)
    date_end = fields.Date(required=True, tracking=True, copy=False)
    # time = fields.Selection([('1','10:00:00'),('2','13:00:00')])
    name_seq = fields.Char(string='Show Reference', required=True, 
        copy=False, readonly=True, index=True, default=lambda self: _('New'))
    seats_limited = fields.Boolean(string='Limit Booking', tracking=True)
    seats_max = fields.Integer(default=-1)
    note = fields.Text(string='Description')
    ticket_id = fields.One2many('theater.booking', 'show_id')
    # state = fields.Selection(related='ticket_id.state')
    bookingdate = fields.One2many('theater.booking', 'show_id')

    active = fields.Boolean(default=True)
    bookingcounter = fields.Integer(string="Total Bookings", compute="compute_tickets")
    seats_left = fields.Integer()

    stage_id = fields.Many2one("configuration.stages", string="Stages")
    stage_active = fields.Selection(related="stage_id.stage_active")
    days = fields.Integer(related="stage_id.days")

    def name_get(self):
        return [(show.id, "%s [%s - %s]" % (show.movie_id.name,show.date_begin,show.date_end)) for show in self]

    @api.model
    def create(self, vals):
        vals['name_seq'] = self.env['ir.sequence'].next_by_code('theater.show.sequence') or _('New')
        result = super(TheaterShows, self).create(vals)
        return result

    @api.depends('ticket_id')
    def compute_tickets(self):
        self.bookingcounter = 0
        # print("SEARCH : ",self.env['theater.booking'].search([('show_id','=',self.movie_id.id),('state','in',['open'])]))
        # print("BROWSE :", self.env['theater.booking'].browse(ids))
        # print("SELF TICKET_ID",self.env['theater.booking'].search_count([('show_id','=',self.movie_id.id),('state','in',['open'])]))
        for rec in self:
            if rec.ticket_id:
                count = sum(rec.env['theater.booking'].search([('show_id.id','=',self.id),('state','in',['open'])]).mapped('seats_qty'))
                rec.bookingcounter = count
                rec.seats_left = rec.seats_max - count

    @api.constrains('date_begin')
    def onchange_date(self):
        records = self.search([])
        print(records)
        for rec in records:
            if rec.date_begin:
                print("ON CHANGE DATE CALLED")
                fmt = '%Y-%m-%d'
                date_begin = rec.date_begin.strftime(fmt)
                date_end = rec.date_end.strftime(fmt)
                current_date = datetime.today().strftime(fmt)
                d1 = datetime.strptime(current_date, fmt)
                d2 = datetime.strptime(date_begin,fmt)
                d3 = datetime.strptime(date_end,fmt) 

                stages = self.env['configuration.stages'].search([])
                dict_stages = dict(zip(stages.mapped('id'),stages.mapped('stage_active')))
                stage = self.env['configuration.stages'].search([('stage_active','=','days_before')])
                if ((d2 - d1).days < 0) and ((d3 - d1).days > 0):
                    if 'days_between' in dict_stages.values():
                        rec.write({'stage_id':list(dict_stages.keys())[list(dict_stages.values()).index('days_between')]})
                elif (d2 - d1).days > 0:
                    res = dict(zip(stage.mapped('id'),stage.mapped('days')))
                    res1 = dict(sorted(res.items(), key=lambda item: item[1]))
                    for x in res1:
                        if res[x] >= ((d2 - d1).days):
                            rec.write({'stage_id':x})
                            break
                else:
                    if 'days_after' in dict_stages.values():
                        rec.write({'stage_id':list(dict_stages.keys())[list(dict_stages.values()).index('days_after')]})











