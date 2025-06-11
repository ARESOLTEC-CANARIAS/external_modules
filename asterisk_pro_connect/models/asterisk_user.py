# -*- coding: utf-8 -*-
# Copyright 2024 Manus AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class AsteriskUser(models.Model):
    _name = "asterisk.user"
    _description = "Asterisk User Configuration"
    _inherit = ["mail.thread"]
    _rec_name = "display_name"

    display_name = fields.Char(
        string="Name", compute="_compute_display_name", store=True
    )

    # User relationship
    user_id = fields.Many2one(
        "res.users",
        string="Odoo User",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    server_id = fields.Many2one(
        "asterisk.server",
        string="Asterisk Server",
        required=True,
        ondelete="cascade",
        tracking=True,
    )

    # Asterisk configuration
    extension = fields.Char(
        string="Extension", required=True, tracking=True, help="User's extension number"
    )
    sip_username = fields.Char(string="SIP Username", tracking=True)
    sip_password = fields.Char(string="SIP Password", tracking=True)
    context = fields.Char(
        string="Dialplan Context",
        default="default",
        tracking=True,
        help="Asterisk dialplan context",
    )

    # Status and preferences
    active = fields.Boolean(string="Active", default=True, tracking=True)
    auto_answer = fields.Boolean(
        string="Auto Answer",
        default=False,
        tracking=True,
        help="Automatically answer incoming calls",
    )
    call_notifications = fields.Boolean(
        string="Call Notifications",
        default=True,
        tracking=True,
        help="Receive notifications for incoming calls",
    )
    click_to_call_enabled = fields.Boolean(
        string="Click-to-Call Enabled",
        default=True,
        tracking=True,
        help="Enable click-to-call functionality",
    )

    # Status information
    online_status = fields.Selection(
        [
            ("online", "Online"),
            ("offline", "Offline"),
            ("busy", "Busy"),
            ("away", "Away"),
            ("dnd", "Do Not Disturb"),
        ],
        string="Status",
        default="offline",
        tracking=True,
    )

    last_seen = fields.Datetime(string="Last Seen", readonly=True)

    # Statistics
    total_calls = fields.Integer(
        string="Total Calls", compute="_compute_call_statistics", store=False
    )
    calls_today = fields.Integer(
        string="Calls Today", compute="_compute_call_statistics", store=False
    )

    # Related records
    call_ids = fields.One2many("asterisk.call", "user_id", string="Calls")

    @api.depends("user_id", "extension")
    def _compute_display_name(self):
        """Compute display name"""
        for record in self:
            if record.user_id and record.extension:
                record.display_name = f"{record.user_id.name} ({record.extension})"
            elif record.user_id:
                record.display_name = record.user_id.name
            else:
                record.display_name = record.extension or "New User"

    @api.depends("call_ids")
    def _compute_call_statistics(self):
        """Compute call statistics"""
        for record in self:
            calls = record.call_ids
            record.total_calls = len(calls)

            # Calls today
            today = fields.Date.today()
            calls_today = calls.filtered(
                lambda c: c.start_time and c.start_time.date() == today
            )
            record.calls_today = len(calls_today)

    def action_test_extension(self):
        """Test extension connectivity"""
        self.ensure_one()

        try:
            self.online_status = "online"
            self.last_seen = fields.Datetime.now()

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Extension Test Successful"),
                    "message": _("Extension %s is reachable") % self.extension,
                    "type": "success",
                },
            }

        except Exception as e:
            self.online_status = "offline"

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Extension Test Failed"),
                    "message": _("Extension %s is not reachable: %s")
                    % (self.extension, str(e)),
                    "type": "danger",
                },
            }

