# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin_markup_percent = fields.Float(
        "Markup (%)", compute='_compute_margin', store=True, aggregator="avg")

    @api.depends('order_line.margin', 'amount_untaxed')
    def _compute_margin(self):
        super()._compute_margin()
        for order in self:
            # Calculate total cost from order lines
            cost_total = sum(
                (line.purchase_price * (line.qty_delivered or line.product_uom_qty))
                for line in order.order_line
                if not line.display_type
            )
            order.margin_markup_percent = order.margin / cost_total if cost_total else 0.0
