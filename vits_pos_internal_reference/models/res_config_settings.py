# -*- coding: utf-8 -*-
###############################################################################
# Author      : Varanval IT Solutions
# Copyright   : (c) 2025 Varanval IT Solutions. All Rights Reserved.
#
# This software and associated files are the copyrighted property of Varanval IT Solutions.
# Unauthorized copying, redistribution, or modification of any part of this code
# is strictly prohibited unless expressly permitted by the author.
#
# This module is a paid product. It is licensed for use only by the customer
# who has purchased it, and only for the number of users specified at purchase.
#
# For licensing inquiries, contact: markvaranval@gmail.com
###############################################################################
from odoo import fields, models,api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_default_code_pos_screen = fields.Boolean(string="Product Default Code on POS Screen",)
    allow_default_code_receipt = fields.Boolean(string="Product Default Code on Order Receipt",)

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('res.config.settings.allow_default_code_pos_screen', self.allow_default_code_pos_screen)
        param.set_param('res.config.settings.allow_default_code_receipt', self.allow_default_code_receipt)

        _logger.info(
            f"[SET] allow_default_code_pos_screen = {self.allow_default_code_pos_screen}, {self.allow_default_code_receipt}")

    def get_values(self):
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo()

        res.update(
            allow_default_code_pos_screen=param.get_param('res.config.settings.allow_default_code_pos_screen'),
            allow_default_code_receipt=param.get_param('res.config.settings.allow_default_code_receipt')
        )
        _logger.info(
            f"[GET] allow_default_code_pos_screen = {self.allow_default_code_pos_screen}, {self.allow_default_code_receipt}")
        return res