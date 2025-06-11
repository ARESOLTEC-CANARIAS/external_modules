# -*- coding: utf-8 -*-
# Copyright 2024 Manus AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    # Asterisk configuration
    asterisk_user_ids = fields.One2many(
        "asterisk.user", "user_id", string="Asterisk Configurations"
    )

    # Call preferences
    call_notifications_enabled = fields.Boolean(
        string="Enable Call Notifications",
        default=True,
        help="Receive browser notifications for incoming calls",
    )
    click_to_call_enabled = fields.Boolean(
        string="Enable Click-to-Call",
        default=True,
        help="Enable click-to-call buttons in forms",
    )

    # Call statistics (computed)
    total_calls_count = fields.Integer(
        string="Total Calls", compute="_compute_call_statistics", store=False
    )
    calls_today_count = fields.Integer(
        string="Calls Today", compute="_compute_call_statistics", store=False
    )

    @api.depends("asterisk_user_ids")
    def _compute_call_statistics(self):
        """Compute call statistics for this user"""
        for record in self:
            # Get all calls for this user
            calls = self.env["asterisk.call"].search([("user_id", "=", record.id)])

            record.total_calls_count = len(calls)

            # Calls today
            today = fields.Date.today()
            calls_today = calls.filtered(
                lambda c: c.start_time and c.start_time.date() == today
            )
            record.calls_today_count = len(calls_today)

    def action_view_my_calls(self):
        """View all calls for this user"""
        self.ensure_one()
        return {
            "name": _("My Calls"),
            "type": "ir.actions.act_window",
            "res_model": "asterisk.call",
            "view_mode": "tree,form",
            "domain": [("user_id", "=", self.id)],
            "context": {"default_user_id": self.id},
        }

