# -*- coding: utf-8 -*-
# Copyright 2024 Manus AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Call statistics
    total_calls = fields.Integer(
        string="Total Calls", compute="_compute_call_statistics", store=False
    )
    last_call_date = fields.Datetime(
        string="Last Call", compute="_compute_call_statistics", store=False
    )

    # Related records
    call_ids = fields.One2many("asterisk.call", "partner_id", string="Calls")

    @api.depends("call_ids")
    def _compute_call_statistics(self):
        """Compute call statistics for this partner"""
        for record in self:
            calls = record.call_ids
            record.total_calls = len(calls)

            # Last call date
            if calls:
                record.last_call_date = max(calls.mapped("start_time"))
            else:
                record.last_call_date = False

    def action_make_call(self):
        """Make a call to this partner"""
        self.ensure_one()

        # Get user's Asterisk configuration
        user_config = self.env["asterisk.user"].search(
            [("user_id", "=", self.env.user.id)], limit=1
        )

        if not user_config:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Configuration Required"),
                    "message": _("Please configure your Asterisk settings first"),
                    "type": "warning",
                },
            }

        # Determine phone number to call
        phone_number = self.phone or self.mobile
        if not phone_number:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("No Phone Number"),
                    "message": _("This contact has no phone number"),
                    "type": "warning",
                },
            }

        return {
            "type": "ir.actions.act_window",
            "res_model": "asterisk.call.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": self.id,
                "default_phone_number": phone_number,
                "default_user_id": self.env.user.id,
            },
        }

    def action_view_calls(self):
        """View all calls for this partner"""
        self.ensure_one()
        return {
            "name": _("Calls - %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "asterisk.call",
            "view_mode": "tree,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }

