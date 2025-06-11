# -*- coding: utf-8 -*-
# Copyright 2024 Manus AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AsteriskCall(models.Model):
    _name = "asterisk.call"
    _description = "Call Detail Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_time desc"
    _rec_name = "display_name"

    # Basic call information
    display_name = fields.Char(
        string="Call", compute="_compute_display_name", store=True
    )
    unique_id = fields.Char(
        string="Unique ID",
        required=True,
        index=True,
        help="Unique identifier for this call from Asterisk",
    )
    server_id = fields.Many2one(
        "asterisk.server",
        string="Server",
        required=True,
        ondelete="cascade",
    )

    # Call participants
    caller_number = fields.Char(string="Caller Number", index=True, tracking=True)
    caller_name = fields.Char(string="Caller Name", tracking=True)
    called_number = fields.Char(string="Called Number", index=True, tracking=True)
    called_name = fields.Char(string="Called Name", tracking=True)

    # Related records
    partner_id = fields.Many2one(
        "res.partner",
        string="Contact",
        index=True,
        tracking=True,
        help="Contact associated with this call",
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        index=True,
        tracking=True,
        help="Odoo user involved in this call",
    )
    lead_id = fields.Many2one(
        "crm.lead",
        string="Opportunity",
        tracking=True,
        help="CRM opportunity associated with this call",
    )

    # Call details
    direction = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound")],
        string="Direction",
        required=True,
        index=True,
        tracking=True,
    )

    status = fields.Selection(
        [
            ("ringing", "Ringing"),
            ("answered", "Answered"),
            ("busy", "Busy"),
            ("no_answer", "No Answer"),
            ("failed", "Failed"),
            ("ended", "Ended"),
        ],
        string="Status",
        default="ringing",
        tracking=True,
        index=True,
    )

    # Timing information
    start_time = fields.Datetime(
        string="Start Time", required=True, index=True, tracking=True
    )
    answer_time = fields.Datetime(string="Answer Time", tracking=True)
    end_time = fields.Datetime(string="End Time", tracking=True)

    # Computed durations
    ring_duration = fields.Integer(
        string="Ring Duration (seconds)",
        compute="_compute_durations",
        store=True,
        help="Time from start to answer",
    )
    talk_duration = fields.Integer(
        string="Talk Duration (seconds)",
        compute="_compute_durations",
        store=True,
        help="Time from answer to end",
    )
    total_duration = fields.Integer(
        string="Total Duration (seconds)",
        compute="_compute_durations",
        store=True,
        help="Total call duration",
    )

    # Human readable durations
    ring_duration_display = fields.Char(
        string="Ring Duration", compute="_compute_duration_display", store=True
    )
    talk_duration_display = fields.Char(
        string="Talk Duration", compute="_compute_duration_display", store=True
    )
    total_duration_display = fields.Char(
        string="Total Duration", compute="_compute_duration_display", store=True
    )

    # Additional information
    recording_id = fields.Many2one(
        "asterisk.recording", string="Recording", help="Call recording if available"
    )
    notes = fields.Text(string="Notes", tracking=True)
    tags = fields.Char(string="Tags", help="Comma-separated tags for categorization")

    # Technical details
    channel = fields.Char(string="Channel", help="Asterisk channel information")
    context = fields.Char(string="Context", help="Asterisk dialplan context")
    extension = fields.Char(string="Extension", help="Called extension")

    # Quality metrics
    quality_score = fields.Selection(
        [
            ("1", "Poor"),
            ("2", "Fair"),
            ("3", "Good"),
            ("4", "Very Good"),
            ("5", "Excellent"),
        ],
        string="Call Quality",
    )

    # Flags
    is_internal = fields.Boolean(
        string="Internal Call", compute="_compute_call_type", store=True
    )
    is_missed = fields.Boolean(
        string="Missed Call", compute="_compute_call_type", store=True
    )
    has_recording = fields.Boolean(
        string="Has Recording", compute="_compute_has_recording", store=True
    )

    @api.depends("caller_number", "called_number", "direction", "start_time")
    def _compute_display_name(self):
        """Compute display name for the call"""
        for record in self:
            if record.direction == "inbound":
                name = f"📞 {record.caller_number or 'Unknown'}"
                if record.partner_id:
                    name += f" ({record.partner_id.name})"
            else:
                name = f"📱 {record.called_number or 'Unknown'}"
                if record.partner_id:
                    name += f" ({record.partner_id.name})"

            if record.start_time:
                name += f" - {record.start_time.strftime('%Y-%m-%d %H:%M')}"

            record.display_name = name

    @api.depends("start_time", "answer_time", "end_time")
    def _compute_durations(self):
        """Compute call durations"""
        for record in self:
            record.ring_duration = 0
            record.talk_duration = 0
            record.total_duration = 0

            if record.start_time:
                if record.answer_time:
                    delta = record.answer_time - record.start_time
                    record.ring_duration = int(delta.total_seconds())

                if record.end_time:
                    delta = record.end_time - record.start_time
                    record.total_duration = int(delta.total_seconds())

                    if record.answer_time:
                        delta = record.end_time - record.answer_time
                        record.talk_duration = int(delta.total_seconds())

    @api.depends("ring_duration", "talk_duration", "total_duration")
    def _compute_duration_display(self):
        """Compute human readable duration displays"""
        for record in self:
            record.ring_duration_display = record._format_duration(
                record.ring_duration
            )
            record.talk_duration_display = record._format_duration(
                record.talk_duration
            )
            record.total_duration_display = record._format_duration(
                record.total_duration
            )

    @api.depends("status", "direction", "answer_time")
    def _compute_call_type(self):
        """Compute call type flags"""
        for record in self:
            # Internal call detection (simplified)
            record.is_internal = False  # Would implement actual logic

            # Missed call detection
            record.is_missed = (
                record.direction == "inbound"
                and record.status in ["no_answer", "busy", "failed"]
                and not record.answer_time
            )

    @api.depends("recording_id")
    def _compute_has_recording(self):
        """Check if call has recording"""
        for record in self:
            record.has_recording = bool(record.recording_id)

    def _format_duration(self, seconds):
        """Format duration in seconds to human readable format"""
        if not seconds:
            return "00:00"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    @api.model
    def create_call(self, vals):
        """Create a new call record with automatic partner detection"""
        # Auto-detect partner based on phone number
        if not vals.get("partner_id"):
            phone_number = (
                vals.get("caller_number")
                if vals.get("direction") == "inbound"
                else vals.get("called_number")
            )
            if phone_number:
                partner = self._find_partner_by_phone(phone_number)
                if partner:
                    vals["partner_id"] = partner.id

        # Auto-detect user based on extension or phone number
        if not vals.get("user_id"):
            user = self._find_user_by_call_info(vals)
            if user:
                vals["user_id"] = user.id

        return self.create(vals)

    def _find_partner_by_phone(self, phone_number):
        """Find partner by phone number"""
        if not phone_number:
            return False

        # Clean phone number
        clean_number = (
            phone_number.replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        # Search in partner phone fields
        partner = self.env["res.partner"].search(
            [
                "|",
                "|",
                ("phone", "ilike", clean_number),
                ("mobile", "ilike", clean_number),
                ("phone", "ilike", phone_number),
            ],
            limit=1,
        )

        return partner

    def _find_user_by_call_info(self, vals):
        """Find user based on call information"""
        # This would implement logic to find the user based on
        # extension, channel, or other call information
        return False

    def action_create_opportunity(self):
        """Create CRM opportunity from this call"""
        self.ensure_one()

        if self.lead_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "crm.lead",
                "res_id": self.lead_id.id,
                "view_mode": "form",
                "target": "current",
            }

        # Create new opportunity
        lead_vals = {
            "name": f"Call from {self.caller_number or self.called_number}",
            "partner_id": self.partner_id.id if self.partner_id else False,
            "phone": (
                self.caller_number
                if self.direction == "inbound"
                else self.called_number
            ),
            "description": f"Opportunity created from call on {self.start_time}",
            "user_id": self.user_id.id if self.user_id else self.env.user.id,
        }

        lead = self.env["crm.lead"].create(lead_vals)
        self.lead_id = lead.id

        return {
            "type": "ir.actions.act_window",
            "res_model": "crm.lead",
            "res_id": lead.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_add_note(self):
        """Add note to call"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "asterisk.call.note.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_call_id": self.id},
        }

    def action_play_recording(self):
        """Play call recording"""
        self.ensure_one()
        if not self.recording_id:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("No Recording"),
                    "message": _("This call has no recording available"),
                    "type": "warning",
                },
            }

        return self.recording_id.action_play()

    @api.model
    def get_call_statistics(self, domain=None):
        """Get call statistics for dashboard"""
        if domain is None:
            domain = []

        calls = self.search(domain)

        return {
            "total_calls": len(calls),
            "inbound_calls": len(calls.filtered(lambda c: c.direction == "inbound")),
            "outbound_calls": len(calls.filtered(lambda c: c.direction == "outbound")),
            "answered_calls": len(calls.filtered(lambda c: c.status == "answered")),
            "missed_calls": len(calls.filtered(lambda c: c.is_missed)),
            "avg_talk_duration": (
                sum(calls.mapped("talk_duration")) / len(calls) if calls else 0
            ),
        }

