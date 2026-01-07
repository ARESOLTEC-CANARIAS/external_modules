
from odoo import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _set_addon_settings(self):
        assembly_id = self.env.ref('binhex_andamios.binhex_scaffold_assembly').id
        disassembly_id = self.env.ref('binhex_andamios.binhex_scaffold_disassembly').id
        renting_id = self.env.ref('binhex_andamios.binhex_scaffold_renting').id
        extension_id = self.env.ref('binhex_andamios.binhex_scaffold_extension').id
        daysxm_id = self.env.ref('binhex_andamios.binhex_product_uom_day_cubic_meters').id

        self.search([]).write({
            "scaffold_services": [(6, 0, [assembly_id, disassembly_id, renting_id, extension_id])],
            "day_udm_ids": [(6, 0, [daysxm_id])]
        })

    day_udm_ids = fields.Many2many('uom.uom', string='Day UdMs')
    scaffold_services = fields.Many2many('product.template', string='Scaffold services')
