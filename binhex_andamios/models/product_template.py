from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class AndamiosProducts(models.Model):
    _inherit = 'product.template'

    scaffold_service_type = fields.Selection([
        ('assembly', 'Assembly'),
        ('disassembly', 'Disassembly'),
        ('renting', 'Renting'),
        ('extension', 'Extension'),
    ], string='Scaffold service type')
