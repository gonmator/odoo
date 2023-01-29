from odoo import api, exceptions, fields, models


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection(selection=[('new', 'New'), ('offer_received', 'Offer Received'),
                                        ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'),
                                        ('canceled', 'Canceled')],
                             required=True, copy=False, default='new')
    tag_ids = fields.Many2many(comodel_name='estate.property.tag')
    property_type_id = fields.Many2one(comodel_name='estate.property.type')

    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    best_offer = fields.Float(compute='_compute_highest_offer_price')

    description = fields.Text()
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=[('north', 'North'), ('south', 'South'), ('east', 'East'),
                                                     ('west', 'West')])
    total_area = fields.Integer(compute='_compute_total_area')

    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_id')

    salesperson_id = fields.Many2one(string='Salesman', default=lambda self: self.env.user, comodel_name='res.users')
    buyer_id = fields.Many2one(comodel_name='res.partner', copy=False)

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids')
    def _compute_highest_offer_price(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped('price'))

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise exceptions.UserError('Canceled properties cannot be sold.')
            record.state = 'sold'
        return True

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise exceptions.UserError('Sold properties cannot be cancelled.')
            record.state = 'canceled'
        return True
