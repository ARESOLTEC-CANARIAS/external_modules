# -*- coding: utf-8 -*-
# Copyright 2024 Manus AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class AsteriskEvent(models.Model):
    _name = "asterisk.event"
    _description = "Asterisk Event"
    _order = "create_date desc"
    _log_access = False

    name = fields.Char(string="Event Name", required=True, index=True)
    event_type = fields.Selection(
        [
            ("call_start", "Call Start"),
            ("call_answer", "Call Answer"),
            ("call_end", "Call End"),
            ("call_hold", "Call Hold"),
            ("call_transfer", "Call Transfer"),
            ("registration", "Registration"),
            ("peer_status", "Peer Status"),
            ("system", "System Event"),
            ("other", "Other"),
        ],
        string="Event Type",
        required=True,
        index=True,
    )

    server_id = fields.Many2one(
        "asterisk.server",
        string="Server",
        required=True,
        ondelete="cascade",
        index=True,
    )

    call_id = fields.Many2one(
        "asterisk.call", string="Related Call", ondelete="cascade", index=True
    )

    # Event data
    event_data = fields.Text(string="Event Data", help="Raw event data from Asterisk")

    # Parsed fields
    channel = fields.Char(string="Channel")
    unique_id = fields.Char(string="Unique ID", index=True)
    caller_id = fields.Char(string="Caller ID")
    extension = fields.Char(string="Extension")

    # Status and processing
    processed = fields.Boolean(string="Processed", default=False, index=True)
    processing_error = fields.Text(string="Processing Error")

    # Timestamps
    event_timestamp = fields.Datetime(
        string="Event Timestamp", required=True, index=True
    )


class AsteriskChannel(models.Model):
    _name = "asterisk.channel"
    _description = "Asterisk Channel"
    _order = "create_date desc"

    name = fields.Char(string="Channel Name", required=True, index=True)
    unique_id = fields.Char(string="Unique ID", index=True)
    server_id = fields.Many2one(
        "asterisk.server", string="Server", required=True, ondelete="cascade"
    )
    call_id = fields.Many2one("asterisk.call", string="Call", ondelete="cascade")

    # Channel details
    state = fields.Selection(
        [
            ("down", "Down"),
            ("reserved", "Reserved"),
            ("offhook", "Off Hook"),
            ("dialing", "Dialing"),
            ("ring", "Ring"),
            ("ringing", "Ringing"),
            ("up", "Up"),
            ("busy", "Busy"),
            ("dialing_offhook", "Dialing Offhook"),
            ("pre_ring", "Pre Ring"),
        ],
        string="State",
        default="down",
    )

    caller_id = fields.Char(string="Caller ID")
    connected_line = fields.Char(string="Connected Line")
    context = fields.Char(string="Context")
    extension = fields.Char(string="Extension")
    priority = fields.Char(string="Priority")

    # Timestamps
    created_time = fields.Datetime(string="Created Time", default=fields.Datetime.now)
    hangup_time = fields.Datetime(string="Hangup Time")

