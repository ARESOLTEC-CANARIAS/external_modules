# -*- coding: utf-8 -*-
# Copyright 2024 Manus AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

{
    "name": "Asterisk Pro Connect",
    "version": "18.0.1.0.0",
    "category": "Phone",
    "summary": "Professional Asterisk integration for Odoo",
    "description": """
Asterisk Pro Connect
====================

Professional Asterisk integration module for Odoo with advanced features.

Features:
---------
* Click-to-call from contacts and opportunities
* Advanced call logging and history
* Real-time call notifications
* User dashboard with call statistics
* CRM integration with automatic opportunity creation
* Modern REST API
* Compatible with Asterisk 18 standard
* Clean OCA-style structure

Technical Features:
------------------
* Compatible with Asterisk 18+
* Responsive web interface
* Real-time WebSocket notifications
* RESTful API with documentation
* Unit tests included
* Internationalization support
* Accessibility compliant
    """,
    "author": "Manus AI",
    "website": "https://github.com/manus-ai/asterisk-pro-connect",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "phone_validation",
        "crm",
        "contacts",
        "web",
    ],
    "external_dependencies": {
        "python": [
            "asterisk-ami",
            "phonenumbers",
        ],
    },
    "data": [
        # Security
        "security/asterisk_security.xml",
        "security/ir.model.access.csv",
        
        # Data
        "data/asterisk_server_data.xml",
        "data/asterisk_event_data.xml",
        "data/ir_cron_data.xml",
        
        # Views
        "views/asterisk_server_views.xml",
        "views/asterisk_call_views.xml",
        "views/asterisk_user_views.xml",
        "views/asterisk_recording_views.xml",
        "views/res_partner_views.xml",
        "views/res_users_views.xml",
        "views/crm_lead_views.xml",
        "views/asterisk_menus.xml",
        
        # Wizards
        "wizard/call_wizard_views.xml",
        
        # Reports
        "reports/call_report_views.xml",
    ],
    "demo": [
        "demo/asterisk_server_demo.xml",
        "demo/asterisk_call_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "asterisk_pro_connect/static/src/scss/asterisk_pro.scss",
            "asterisk_pro_connect/static/src/js/click_to_call.js",
            "asterisk_pro_connect/static/src/js/call_notifications.js",
            "asterisk_pro_connect/static/src/js/user_panel.js",
            "asterisk_pro_connect/static/src/js/phone_widget.js",
            "asterisk_pro_connect/static/src/xml/click_to_call.xml",
            "asterisk_pro_connect/static/src/xml/call_notifications.xml",
            "asterisk_pro_connect/static/src/xml/user_panel.xml",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "development_status": "Beta",
    "maintainers": ["manus-ai"],
}

