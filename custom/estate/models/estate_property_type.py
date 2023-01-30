from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _sql_constraints = [('check_type_name', 'UNIQUE(name)', 'The type name must be unique.')]
    _order = 'sequence, name'

    name = fields.Char(required=True)
    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='property_type_id')
    sequence = fields.Integer('Sequence', default=1)
