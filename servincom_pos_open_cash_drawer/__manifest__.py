# Copyright 2026 SERVINCOM SOLUCIONES, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "SERVINCOM POS Open Cash Drawer",
    "version": "16.0.1.0.0",
    "summary": "Open the configured POS cash drawer from the product screen",
    "category": "Point of Sale",
    "author": "SERVINCOM SOLUCIONES, S.L.",
    "license": "AGPL-3",
    "depends": [
        "point_of_sale",
    ],
    "assets": {
        "point_of_sale.assets": [
            "servincom_pos_open_cash_drawer/static/src/js/open_cash_drawer_button.js",
            "servincom_pos_open_cash_drawer/static/src/xml/open_cash_drawer_button.xml",
        ],
    },
    "installable": True,
    "application": False,
}
