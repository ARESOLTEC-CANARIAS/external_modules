# -*- coding: utf-8 -*-
###############################################################################
# Author      : Varanval IT Solutions
# Copyright   : (c) 2025 Varanval IT Solutions. All Rights Reserved.
#
# This software and associated files are the copyrighted property of Varanval IT Solutions.
# Unauthorized copying, redistribution, or modification of any part of this code
# is strictly prohibited unless expressly permitted by the author.
#
# This module is a paid product. It is licensed for use only by the customer
# who has purchased it, and only for the number of users specified at purchase.
#
# For licensing inquiries, contact: markvaranval@gmail.com
###############################################################################
{
    'name': 'POS Internal Reference | POS Default Code',
    'version': '18.1.1',
    'category': 'Point of Sale',
    'summary': "pos internal references | odoo pos internal reference | pos product internal reference | pos product default code | show internal reference in pos | display sku in pos | pos show sku | odoo pos sku display | internal reference in pos screen | pos product code display | odoo pos product code | pos internal code | show product code in pos | pos receipt internal reference | pos order receipt sku | print internal reference on pos receipt | odoo pos receipt product code | pos product identification | pos billing accuracy | odoo pos customization | pos screen customization | pos product info display | odoo pos product reference | pos default code visibility | odoo pos improve billing | pos cashier efficiency | pos product lookup | odoo pos ui enhancement | pos inventory reference | pos product sku | odoo pos internal sku | pos product reference module | odoo pos addon | pos product management | odoo pos retail | pos shop management",
    'description': """pos internal references | odoo pos internal reference | pos product internal reference | pos product default code | show internal reference in pos | display sku in pos | pos show sku | odoo pos sku display | internal reference in pos screen | pos product code display | odoo pos product code | pos internal code | show product code in pos | pos receipt internal reference | pos order receipt sku | print internal reference on pos receipt | odoo pos receipt product code | pos product identification | pos billing accuracy | odoo pos customization | pos screen customization | pos product info display | odoo pos product reference | pos default code visibility | odoo pos improve billing | pos cashier efficiency | pos product lookup | odoo pos ui enhancement | pos inventory reference | pos product sku | odoo pos internal sku | pos product reference module | odoo pos addon | pos product management | odoo pos retail | pos shop management""",
    'depends': ['base', 'point_of_sale'],
    'keywords': [
            'pos internal references',
            'odoo pos internal reference',
            'pos product internal reference',
            'pos product default code',
            'show internal reference in pos',
            'display sku in pos',
            'pos show sku',
            'odoo pos sku display',
            'internal reference in pos screen',
            'pos product code display',
            'odoo pos product code',
            'pos internal code',
            'show product code in pos',
            'pos receipt internal reference',
            'pos order receipt sku',
            'print internal reference on pos receipt',
            'odoo pos receipt product code',
            'pos product identification',
            'pos billing accuracy',
            'odoo pos customization',
            'pos screen customization',
            'pos product info display',
            'odoo pos product reference',
            'pos default code visibility',
            'odoo pos improve billing',
            'pos cashier efficiency',
            'pos product lookup',
            'odoo pos ui enhancement',
            'pos inventory reference',
            'pos product sku',
            'odoo pos internal sku',
            'pos product reference module',
            'odoo pos addon',
            'pos product management',
            'odoo pos retail',
            'pos shop management',
        ],
    'author': 'Varanval IT Solutions',
    'company': 'Varanval IT Solutions',
    'price': '4.00',
    'currency': 'USD',
    'data': [
        'views/res_config_settings.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'vits_pos_internal_reference/static/src/js/inherit_order_line.js',
             'vits_pos_internal_reference/static/src/js/inherit_product_screen.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}