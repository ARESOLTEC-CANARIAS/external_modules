# -*- coding: utf-8 -*-
from odoo import fields, models

class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    default_partner_id = fields.Many2one('res.partner', string="Select Customer")

class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_default_partner_id = fields.Many2one('res.partner',related="pos_config_id.default_partner_id",readonly=False, string="Default Customer")
