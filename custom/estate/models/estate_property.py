from odoo import api, exceptions, fields, models, tools


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0.0)', 'The expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0.0)', 'The selling price must be positive.')
    ]
    _order = 'id desc'

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

    @api.depends('offer_ids')
    def _compute_highest_offer_price(self):
        for record in self:
            offers = record.offer_ids.mapped('price')
            if len(offers):
                record.best_offer = max(offers)
            else:
                record.best_offer = 0.0

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            # if selling_price == 0.0 that means not offer has been accepted.
            if not tools.float_is_zero(record.selling_price, precision_rounding=0.01):
                if tools.float_compare(record.selling_price, record.expected_price * 0.9, precision_rounding=0.01) < 0:
                    raise exceptions.ValidationError(
                        'The selling price must be at least 90% of the expected price! '
                        'You must reduce the expected price if you want to accept this offer.')

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.onchange('offer_ids')
    def _onchange_offer_id(self):
        if self.state == 'offer_received' and len(self.offer_ids) == 0:
            self.state = 'new'

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancelled(self):
        if self.state not in ['new' or 'canceled']:
            raise exceptions.UserError('Only new and canceled properties can be deleted.')

    def action_sold(self):
        self.ensure_one()
        if self.state == 'canceled':
            raise exceptions.UserError('Canceled properties cannot be sold.')
        self.state = 'sold'
        return True

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'sold':
            raise exceptions.UserError('Sold properties cannot be cancelled.')
        self.state = 'canceled'
        return True

    def _is_there_offer_accepted(self, property_id):
        property_offers = self.env['estate.property.offer'].search([('property_id', '=', property_id)])
        return any(r.status == 'accepted' for r in property_offers)
