# -*- coding: utf-8 -*-
{
    'name': 'Sale Margin Compute Custom',
    'version': '1.0',
    'category': 'Sales/Sales',
    'summary': 'Add margin over cost (markup) calculation to sale orders',
    'description': """
        This module adds a new field to calculate the margin over cost (markup) 
        in addition to the standard margin over sales price.
    """,
    'author': 'Espais Virtuals Tech SL',
    'depends': ['sale_margin'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
