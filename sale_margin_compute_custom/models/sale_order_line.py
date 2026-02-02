# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_markup_percent = fields.Float(
        "Markup (%)", compute='_compute_margin', store=True, 
        groups="base.group_user", precompute=True)

    @api.depends('price_subtotal', 'product_uom_qty', 'purchase_price')
    def _compute_margin(self):
        super()._compute_margin()
        for line in self:
            # Handle case when line is added from delivery (qty_delivered but no product_uom_qty)
            if line.qty_delivered and not line.product_uom_qty:
                cost_total = line.purchase_price * line.qty_delivered
            else:
                cost_total = line.purchase_price * line.product_uom_qty
            
            line.margin_markup_percent = line.margin / cost_total if cost_total else 0.0
