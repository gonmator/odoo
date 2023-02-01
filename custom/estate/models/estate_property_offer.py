from odoo import api, exceptions, fields, models


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0.0)', 'The offer price must be strictly positive.')
    ]
    _order = 'price desc'

    price = fields.Float()
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one(comodel_name='res.partner', required=True)
    property_id = fields.Many2one(comodel_name='estate.property', required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_deadline', inverse='_inverse_deadline')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

    def action_accept(self):
        if len(self) > 1:
            raise exceptions.UserError('Only one offer can be accepted.')
        # property_id = self.property_id.id
        # property_offers = self.env['estate.property.offer'].search([('property_id', '=', property_id)])
        # if any(r.status == 'accepted' for r in property_offers):
        #     raise exceptions.UserError('An offer has been already accepted.')
        if self.property_id._is_there_offer_accepted(self.property_id.id):
            raise exceptions.UserError('An offer has been already accepted.')
        # we only have one record here
        self.status = 'accepted'
        self.property_id.buyer_id = self.partner_id
        self.property_id.selling_price = self.price
        self.property_id.state = 'offer_accepted'
        return True

    def action_refuse(self):
        for record in self:
            record.status = 'refused'
            self.property_id.buyer_id = None
            self.property_id.selling_price = 0.0
            if not self.property_id._is_there_offer_accepted(self.property_id.id):
                self.property_id.state = 'offer_received'
        return True

    @api.depends('create_date', 'validity')
    def _compute_deadline(self):
        for record in self:
            create_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = fields.Date.add(create_date, days=record.validity)

    def _inverse_deadline(self):
        for record in self:
            create_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.validity = fields.Date.subtract(record.date_deadline - create_date).days
