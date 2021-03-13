from odoo import api, fields, models
from odoo.exceptions import ValidationError

class TheaterMovie(models.Model):
    _name = 'theater.movie'
    _inherit = "mail.thread"
    _description = 'Movies'
    _rec_name = 'name'

    name = fields.Char(string='Show Title', required=True, tracking=0)
    minutes = fields.Integer(string='Total Minutes', tracking=1)
    hours = fields.Float(compute='get_hours')
    language_id = fields.Many2one('res.lang', string="Language", tracking=2)
    director = fields.Char(string='Director', required=True, tracking=3)
    release_date = fields.Date(string='Release Date', tracking=4)
    image = fields.Binary()
    tag_ids = fields.Many2many('tags.categories', string="Tags")
    role = fields.Selection([
        ('hero','Hero'),
        ('villen','Villen')])

    cast_ids = fields.Many2many('movie.cast','movie_id')
    show_id = fields.One2many('theater.show', 'movie_id')

    @api.depends('minutes')
    def get_hours(self):
        self.hours = 0.0
        for rec in self:
            if rec.minutes:
                rec.hours = rec.minutes/60

    @api.constrains('name')
    def _stages_constrains(self):
        names = []
        records = self.read_group([('id', 'not in', [self.id])], \
            ['name'],['name'])
        print("READ_GROUP : ",records)
        for record in records:
            names.append(record['name'].lower())
        for record in self:
            if record.name.lower() in names:
                raise ValidationError("Movie Must be unique in Movies.")