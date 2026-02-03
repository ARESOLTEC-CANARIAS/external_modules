
from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    day_udm_ids = fields.Many2many(related="company_id.day_udm_ids", readonly=False, string='Day UdMs')
    scaffold_services = fields.Many2many(related="company_id.scaffold_services", readonly=False, string='Scaffold services')

    @api.model
    def _set_config_settings(self):
        self.create({
            # "group_subtask_project": True,
            "group_analytic_accounting": True,
            "group_product_variant": True,
            "group_uom": True
        }).execute()
