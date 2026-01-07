from odoo import models


import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    # default_service = fields.Selection([
    #     ('assembly', _('Assembly')),
    #     ('disassembly', _('Disassembly')),
    #     ('renting', _('Renting')),
    # ], string='Default service')

    def _get_customer_product_code(self, partner_id, qty):
        supplier_info = self.env['product.customerinfo'].search([
            ('partner_id', '=', partner_id),
            ('min_qty', '<=', int(qty)),
            '|',
            ('product_id', '=', self.id),
            '&',
            ('product_id', '=', False),
            ('product_tmpl_id', '=', self.id)
        ], order="min_qty desc", limit=1)
        return supplier_info.product_code if supplier_info else ''


# class AndamiosProducts(models.Model):
#     _inherit = 'product.template'

#     scaffold_service_type = fields.Selection([
#         ('assembly', _('Assembly')),
#         ('disassembly', _('Disassembly')),
#         ('renting', _('Renting')),
#         ('extension', _('Extension')),
#     ], string='Scaffold service type')
