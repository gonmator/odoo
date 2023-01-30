from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _sql_constraints = [('check_tag_name', 'UNIQUE(name)', 'The tag name must be unique.')]
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer()
