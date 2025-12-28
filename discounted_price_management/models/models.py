from odoo import models, fields, api


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    price_after_discount = fields.Float(
        string='Unit Price after Disc%',
        compute='_compute_price_after_discount', readeonly=True,
        help="Unit price after applying the discount"
    )

    @api.depends('discount', 'price_unit')
    def _compute_price_after_discount(self):
        for line in self:
            if line.price_unit and line.discount:
                line.price_after_discount = line.price_unit * (1 - line.discount / 100)
            else:
                line.price_after_discount = line.price_unit


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_after_discount = fields.Float(
        string='Unit Price after Disc%',
        compute='_compute_price_after_discount', readeonly=True,
        help="Unit price after applying the discount"
    )

    @api.depends('discount', 'price_unit')
    def _compute_price_after_discount(self):
        for line in self:
            if line.price_unit and line.discount:
                line.price_after_discount = line.price_unit * (1 - line.discount / 100)
            else:
                line.price_after_discount = line.price_unit
