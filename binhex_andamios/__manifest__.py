{
    'name': "Binhex Andamios",

    'summary': """
        Allows to make invoices and sale orders with scaffolds""",

    'description': """
        Allows to make invoices and sale orders with scaffolds, invoices are now calculated based on the cubic meters done in the tasks.
        More information in the index.html of the addon.
    """,

    'author': "Binhex Systems Solution S.L.",
    'website': "http://binhex.es",

    'category': 'Accounting',
    'version': "18.0.1.0.0",

    'depends': ['base',
                'account',
                'purchase',
                'sale',
                'project',
                'sale_timesheet',
                'hr_timesheet',
                'sale_start_end_dates',
                'sale_rental',
                'sale_layout_category_hide_detail',
                'account_payment_partner',
                ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/scaffold_scaffold.xml',
        'views/scaffold_stage.xml',
        'views/scaffold_zone.xml',
        'views/res_partner.xml',
        'views/account_move.xml',
        'views/project.xml',
        'views/sale_order.xml',
        'views/product_product.xml',
        'views/project_project.xml',
        'views/res_config_settings.xml',
        'views/product_template.xml',
        'views/sale_order_portal.xml',
        'views/project_task.xml',
        'data/product.xml',
        'data/stage.xml',
        'data/service_cron.xml',
        'views/menus.xml',
        'views/sequences.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'application': True,
}
