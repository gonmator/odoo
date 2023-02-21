from odoo import Command, models


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        journal_id = self.env['account.journal'].search([('code', '=', 'INV')], limit=1).id
        invoice_line_commission = {'name': 'Commission', 'quantity': 0.06, 'price_unit': self.selling_price}
        invoice_line_admin_fee = {'name': 'Administrative fee', 'quantity': 1, 'price_unit': 100.00}
        self.env['account.move'].create(
            {'partner_id': self.buyer_id.id, 'move_type': 'out_invoice', 'journal_id': journal_id,
             'invoice_line_ids': [Command.create(invoice_line_commission), Command.create(invoice_line_admin_fee)]}
        )

        return super().action_sold()
