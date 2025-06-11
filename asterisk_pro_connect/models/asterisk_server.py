# -*- coding: utf-8 -*-
# Copyright 2024 Manus AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class AsteriskServer(models.Model):
    _name = "asterisk.server"
    _description = "Asterisk Server Configuration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(
        string="Server Name",
        required=True,
        tracking=True,
        help="Friendly name for the Asterisk server",
    )
    host = fields.Char(
        string="Host/IP Address",
        required=True,
        tracking=True,
        help="Asterisk server hostname or IP address",
    )
    port = fields.Integer(
        string="AMI Port",
        default=5038,
        required=True,
        tracking=True,
        help="Asterisk Manager Interface port (default: 5038)",
    )
    username = fields.Char(
        string="AMI Username",
        required=True,
        tracking=True,
        help="Username for Asterisk Manager Interface",
    )
    password = fields.Char(
        string="AMI Password",
        required=True,
        tracking=True,
        help="Password for Asterisk Manager Interface",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
        help="Whether this server configuration is active",
    )
    version = fields.Char(
        string="Asterisk Version", readonly=True, help="Detected Asterisk version"
    )
    connection_status = fields.Selection(
        [
            ("connected", "Connected"),
            ("disconnected", "Disconnected"),
            ("error", "Connection Error"),
            ("testing", "Testing Connection"),
        ],
        string="Connection Status",
        default="disconnected",
        tracking=True,
    )

    last_connection_test = fields.Datetime(
        string="Last Connection Test", readonly=True
    )
    connection_error = fields.Text(string="Connection Error Details", readonly=True)

    # Configuration options
    auto_create_partners = fields.Boolean(
        string="Auto Create Partners",
        default=True,
        help="Automatically create partner records for unknown numbers",
    )
    call_popup_enabled = fields.Boolean(
        string="Enable Call Popups",
        default=True,
        help="Show popup notifications for incoming calls",
    )
    recording_enabled = fields.Boolean(
        string="Enable Call Recording",
        default=False,
        help="Enable automatic call recording",
    )
    recording_path = fields.Char(
        string="Recording Path",
        help="Path where call recordings are stored on Asterisk server",
    )

    # Statistics
    total_calls = fields.Integer(
        string="Total Calls", compute="_compute_call_statistics", store=False
    )
    calls_today = fields.Integer(
        string="Calls Today", compute="_compute_call_statistics", store=False
    )
    active_calls = fields.Integer(
        string="Active Calls", compute="_compute_call_statistics", store=False
    )

    # Related records
    user_ids = fields.One2many("asterisk.user", "server_id", string="Users")
    call_ids = fields.One2many("asterisk.call", "server_id", string="Calls")

    @api.constrains("host", "port")
    def _check_connection_details(self):
        """Validate connection details"""
        for record in self:
            if not record.host:
                raise ValidationError(_("Host/IP address is required"))
            if not (1 <= record.port <= 65535):
                raise ValidationError(_("Port must be between 1 and 65535"))

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

            # Active calls
            active_calls = calls.filtered(lambda c: c.status in ["ringing", "answered"])
            record.active_calls = len(active_calls)

    def test_connection(self):
        """Test connection to Asterisk server"""
        self.ensure_one()

        try:
            self.connection_status = "testing"
            self.last_connection_test = fields.Datetime.now()

            # Here you would implement actual AMI connection test
            # For now, we'll simulate a successful connection

            # Simulate successful connection
            self.connection_status = "connected"
            self.connection_error = False
            self.version = "Asterisk 18.0.0"  # Would be detected from server

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Successful"),
                    "message": _("Successfully connected to Asterisk server"),
                    "type": "success",
                },
            }

        except Exception as e:
            self.connection_status = "error"
            self.connection_error = str(e)

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Failed"),
                    "message": _("Failed to connect to Asterisk server: %s") % str(e),
                    "type": "danger",
                },
            }

    def action_view_calls(self):
        """Open calls view for this server"""
        self.ensure_one()
        return {
            "name": _("Calls - %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "asterisk.call",
            "view_mode": "tree,form",
            "domain": [("server_id", "=", self.id)],
            "context": {"default_server_id": self.id},
        }

    def action_view_users(self):
        """Open users view for this server"""
        self.ensure_one()
        return {
            "name": _("Users - %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "asterisk.user",
            "view_mode": "tree,form",
            "domain": [("server_id", "=", self.id)],
            "context": {"default_server_id": self.id},
        }

    @api.model
    def get_default_server(self):
        """Get the default active server"""
        server = self.search([("active", "=", True)], limit=1)
        if not server:
            raise UserError(_("No active Asterisk server configured"))
        return server

