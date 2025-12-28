# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "POS Invoice and Register Payment",
    "version": "18.0.0.2",
    "category": "Point of Sale",
    "depends": ['base', 'sale', 'point_of_sale'],
    "author": "BROWSEINFO",
    'summary': 'point of sales payment methods pos invoice payment pos accounting payment pos register payment pos voucher payment pos Multiple and partial payments pos payment methods POS payments point of sales payments POS screen register payment on pos advance payment',
    "price": 49,
    "currency": 'EUR',
    "description": """
    pos invoice payment pos accounting payment pos register payment pos voucher payment pos payment 
    pos payment from pos screen invoice payment from POS screen register payment from pos screen
    pay invoice from POS screen accounting payment from POS screen
    point of sale invoice payment point of sale accounting payment point of sale register payment
    point of sale voucher payment point of sale payment payment from point of sale screen
    pos invoice payment from point of sale screen register payment from point of sale screen
    pay invoice from point of sale screen accounting payment from point of sale screen pos multiple invoice payment
    pos mass invoice payment point of sales multiple invoice payment point of sales mass invoice payment
    Purpose :- 
    """,
    "website": "https://www.browseinfo.com/demo-request?app=bi_pos_payment&version=18&edition=Community",
    "data": [
        'security/ir.model.access.csv',
        'views/custom_pos_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # control_buttons
            'bi_pos_payment/static/src/app/screens/product_screen/control_buttons/payment_button/payment_button.js',
            'bi_pos_payment/static/src/app/screens/product_screen/control_buttons/payment_button/payment_button.xml',
            'bi_pos_payment/static/src/app/screens/product_screen/control_buttons/invoice_button/invoice_button.js',
            'bi_pos_payment/static/src/app/screens/product_screen/control_buttons/invoice_button/invoice_button.xml',
            # models
            'bi_pos_payment/static/src/app/store/partner_line.js',
            # dialog
            'bi_pos_payment/static/src/app/utils/register_payment_popup/register_payment_popup.js',
            'bi_pos_payment/static/src/app/utils/register_payment_popup/register_payment_popup.xml',
            'bi_pos_payment/static/src/app/utils/invoice_detail_popup/invoice_detail_popup.js',
            'bi_pos_payment/static/src/app/utils/invoice_detail_popup/invoice_detail_popup.xml',
            'bi_pos_payment/static/src/app/utils/register_invoice_payment_popup/register_invoice_payment_popup.js',
            'bi_pos_payment/static/src/app/utils/register_invoice_payment_popup/register_invoice_payment_popup.xml',
            # screens
            'bi_pos_payment/static/src/app/screens/product_screen/partner_list_screen/partner_list_screen.js',
            'bi_pos_payment/static/src/app/screens/product_screen/partner_list_screen/partner_list_screen.xml',

            'bi_pos_payment/static/src/app/screens/product_screen/partner_list_screen/PaymentReceipt.js',
            'bi_pos_payment/static/src/app/screens/product_screen/partner_list_screen/PaymentReceiptScreen.js',
            'bi_pos_payment/static/src/app/screens/product_screen/partner_list_screen/payment_receipt.xml',

            'bi_pos_payment/static/src/app/screens/product_screen/invoice_screen/invoice_screen.js',
            'bi_pos_payment/static/src/app/screens/product_screen/invoice_screen/invoice_screen.xml',

            'bi_pos_payment/static/src/app/screens/product_screen/invoice_screen/InvoiceReceipt.js',
            'bi_pos_payment/static/src/app/screens/product_screen/invoice_screen/InvoiceReceiptScreen.js',
            'bi_pos_payment/static/src/app/screens/product_screen/invoice_screen/invoice_receipt.xml',

            'bi_pos_payment/static/src/app/screens/product_screen/invoice_screen/invoice_line/invoice_line.js',
            'bi_pos_payment/static/src/app/screens/product_screen/invoice_screen/invoice_line/invoice_line.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    "live_test_url": "https://www.browseinfo.com/demo-request?app=bi_pos_payment&version=18&edition=Community",
    "images": ['static/description/Banner.gif'],
    'license': 'OPL-1',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
