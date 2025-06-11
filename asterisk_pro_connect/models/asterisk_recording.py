# -*- coding: utf-8 -*-
# Copyright 2024 Manus AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class AsteriskRecording(models.Model):
    _name = "asterisk.recording"
    _description = "Call Recording"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    name = fields.Char(string="Recording Name", compute="_compute_name", store=True)

    # Related call
    call_id = fields.Many2one(
        "asterisk.call",
        string="Call",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # File information
    filename = fields.Char(
        string="File Name",
        required=True,
        help="Original filename on Asterisk server",
    )
    file_path = fields.Char(
        string="File Path",
        required=True,
        help="Full path to recording file on Asterisk server",
    )
    file_size = fields.Integer(
        string="File Size (bytes)", help="Size of the recording file in bytes"
    )
    file_format = fields.Selection(
        [
            ("wav", "WAV"),
            ("mp3", "MP3"),
            ("gsm", "GSM"),
            ("g729", "G.729"),
            ("ulaw", "μ-law"),
            ("alaw", "A-law"),
        ],
        string="Format",
        default="wav",
    )

    # Recording details
    duration = fields.Integer(
        string="Duration (seconds)", help="Duration of the recording in seconds"
    )
    duration_display = fields.Char(
        string="Duration", compute="_compute_duration_display", store=True
    )

    # Status and processing
    status = fields.Selection(
        [
            ("recording", "Recording"),
            ("completed", "Completed"),
            ("processing", "Processing"),
            ("ready", "Ready"),
            ("error", "Error"),
        ],
        string="Status",
        default="recording",
        tracking=True,
    )

    # Access and security
    access_token = fields.Char(string="Access Token")
    download_count = fields.Integer(string="Download Count", default=0)

    @api.depends("call_id", "filename")
    def _compute_name(self):
        """Compute recording name"""
        for record in self:
            if record.call_id and record.filename:
                record.name = f"{record.call_id.display_name} - {record.filename}"
            elif record.filename:
                record.name = record.filename
            else:
                record.name = "New Recording"

    @api.depends("duration")
    def _compute_duration_display(self):
        """Compute human readable duration"""
        for record in self:
            if record.duration:
                hours = record.duration // 3600
                minutes = (record.duration % 3600) // 60
                seconds = record.duration % 60

                if hours:
                    record.duration_display = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    record.duration_display = f"{minutes:02d}:{seconds:02d}"
            else:
                record.duration_display = "00:00"

    def action_play(self):
        """Play the recording"""
        self.ensure_one()

        if self.status != "ready":
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Recording Not Ready"),
                    "message": _("This recording is not ready for playback"),
                    "type": "warning",
                },
            }

        # Generate secure URL for playback
        url = f"/asterisk/recording/play/{self.id}"
        if self.access_token:
            url += f"?token={self.access_token}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

