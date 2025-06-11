# -*- coding: utf-8 -*-
# Copyright 2024 Manus AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import json
import logging
from odoo import http, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


class AsteriskController(http.Controller):
    """Main controller for Asterisk integration"""

    @http.route(
        "/asterisk/click_to_call",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def click_to_call(self, phone_number, partner_id=None, lead_id=None):
        """Initiate a click-to-call request"""
        try:
            # Get user's Asterisk configuration
            user_config = request.env["asterisk.user"].search(
                [("user_id", "=", request.env.user.id)], limit=1
            )

            if not user_config:
                return {
                    "success": False,
                    "error": "No Asterisk configuration found for user",
                }

            # Validate phone number
            if not phone_number:
                return {"success": False, "error": "Phone number is required"}

            # Create call record
            call_vals = {
                "unique_id": f"click2call_{request.env.user.id}_{phone_number}",
                "server_id": user_config.server_id.id,
                "user_id": request.env.user.id,
                "direction": "outbound",
                "called_number": phone_number,
                "start_time": http.request.env.context.get("tz"),
                "status": "ringing",
            }

            if partner_id:
                call_vals["partner_id"] = partner_id
            if lead_id:
                call_vals["lead_id"] = lead_id

            call = request.env["asterisk.call"].create(call_vals)

            # Here you would implement actual call initiation
            # For now, we'll simulate success

            return {
                "success": True,
                "call_id": call.id,
                "message": f"Call initiated to {phone_number}",
            }

        except Exception as e:
            _logger.error(f"Error in click_to_call: {str(e)}")
            return {"success": False, "error": str(e)}

    @http.route(
        "/asterisk/call_status/<int:call_id>",
        type="json",
        auth="user",
        methods=["GET"],
    )
    def get_call_status(self, call_id):
        """Get status of a specific call"""
        try:
            call = request.env["asterisk.call"].browse(call_id)
            if not call.exists():
                return {"success": False, "error": "Call not found"}

            return {
                "success": True,
                "status": call.status,
                "duration": call.total_duration,
                "start_time": call.start_time.isoformat() if call.start_time else None,
                "end_time": call.end_time.isoformat() if call.end_time else None,
            }

        except Exception as e:
            _logger.error(f"Error getting call status: {str(e)}")
            return {"success": False, "error": str(e)}

    @http.route(
        "/asterisk/user_config", type="json", auth="user", methods=["GET"]
    )
    def get_user_config(self):
        """Get current user's Asterisk configuration"""
        try:
            user_config = request.env["asterisk.user"].search(
                [("user_id", "=", request.env.user.id)], limit=1
            )

            if not user_config:
                return {"success": False, "error": "No configuration found"}

            return {
                "success": True,
                "config": {
                    "extension": user_config.extension,
                    "server_name": user_config.server_id.name,
                    "click_to_call_enabled": user_config.click_to_call_enabled,
                    "call_notifications": user_config.call_notifications,
                    "online_status": user_config.online_status,
                },
            }

        except Exception as e:
            _logger.error(f"Error getting user config: {str(e)}")
            return {"success": False, "error": str(e)}

    @http.route(
        "/asterisk/call_statistics", type="json", auth="user", methods=["GET"]
    )
    def get_call_statistics(self, period="today"):
        """Get call statistics for current user"""
        try:
            user = request.env.user
            stats = user.get_call_statistics_data(period)

            return {"success": True, "statistics": stats}

        except Exception as e:
            _logger.error(f"Error getting call statistics: {str(e)}")
            return {"success": False, "error": str(e)}

    @http.route(
        "/asterisk/recent_calls", type="json", auth="user", methods=["GET"]
    )
    def get_recent_calls(self, limit=10):
        """Get recent calls for current user"""
        try:
            calls = (
                request.env["asterisk.call"]
                .search(
                    [("user_id", "=", request.env.user.id)],
                    limit=limit,
                    order="start_time desc",
                )
                .read(
                    [
                        "display_name",
                        "direction",
                        "status",
                        "start_time",
                        "total_duration_display",
                        "partner_id",
                    ]
                )
            )

            return {"success": True, "calls": calls}

        except Exception as e:
            _logger.error(f"Error getting recent calls: {str(e)}")
            return {"success": False, "error": str(e)}

    @http.route(
        "/asterisk/recording/play/<int:recording_id>",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def play_recording(self, recording_id, token=None):
        """Stream call recording"""
        try:
            recording = request.env["asterisk.recording"].browse(recording_id)
            if not recording.exists():
                return request.not_found()

            # Verify access token if provided
            if token and recording.access_token != token:
                return request.not_found()

            # Here you would implement actual file streaming
            # For now, return a placeholder response
            return request.make_response(
                "Recording playback not implemented",
                headers=[("Content-Type", "text/plain")],
            )

        except Exception as e:
            _logger.error(f"Error playing recording: {str(e)}")
            return request.not_found()

    @http.route(
        "/asterisk/recording/download/<int:recording_id>",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def download_recording(self, recording_id, token=None):
        """Download call recording"""
        try:
            recording = request.env["asterisk.recording"].browse(recording_id)
            if not recording.exists():
                return request.not_found()

            # Verify access token if provided
            if token and recording.access_token != token:
                return request.not_found()

            # Here you would implement actual file download
            # For now, return a placeholder response
            return request.make_response(
                "Recording download not implemented",
                headers=[
                    ("Content-Type", "application/octet-stream"),
                    ("Content-Disposition", f"attachment; filename={recording.filename}"),
                ],
            )

        except Exception as e:
            _logger.error(f"Error downloading recording: {str(e)}")
            return request.not_found()

