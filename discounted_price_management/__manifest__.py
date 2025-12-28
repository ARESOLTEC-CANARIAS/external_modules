# -*- coding: utf-8 -*-
{
    'name': "Unit Price After Applying Discounts",
    'summary': """This module calculates and displays the unit price after applying discounts on sales orders and 
    invoices.""",
    'author': "Basem Walid",
    'maintainer': "Basem Walid",
    'website': "https://www.linkedin.com/in/basem-walid600/",
    'license': "AGPL-3",
    'sequence': '3',
    'category': 'Accounting',
    'version': '18.0.1.0',
    'depends': ['base', 'sale', 'account', 'sale_management'],
    'data': [
        'views/views.xml',
        'views/inherit_report.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
    'price': 15.99,
    'currency': "USD",
}
