from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AndamiosProducts(models.Model):
    _inherit = 'product.product'

    default_service = fields.Selection([
        ('assembly', 'Assembly'),
        ('disassembly', 'Disassembly'),
        ('renting', 'Renting'),
    ], string='Default service')

    @api.model_create_multi
    def create(self, vals):
        records = self.env['product.product']
        for list in vals:
            record = super(AndamiosProducts, self).create(list)
            self._one_by_default(record)
            records |= record
        return records

    def write(self, vals):
        super(AndamiosProducts, self).write(vals)
        if vals.get('default_service'):
            self._one_by_default()
        return

    def _one_by_default(self, record=False):
        if not record:
            record = self
        busqueda = self.env['product.product'].search([('default_service', '=', self.default_service), ('id', '!=', record.id)])
        for r in busqueda:
            r.default_service = False
