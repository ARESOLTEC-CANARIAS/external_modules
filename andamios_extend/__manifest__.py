{
    'name': "andamios_extend",

    'summary': """
        This addon add a new funcionality for andamios module.
        """,
    'author': "Binhex",
    'website': "https://github.com/BinhexTeam/ateca_custom",
    'category': 'Custom',
    'version': "18.0.1.0.0",
    'license' : 'AGPL-3',

    'depends': [
        'base',
        'binhex_andamios',
        'binhex_andamios_report',
        'project_task_default_stage',
        'product_customerinfo',
        'project_task_material',
    ],

    # 'qweb': [
    #     'static/src/xml/list_view_buttons.xml'
    # ],

    'data': [
        # 'views/assets.xml',
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'data/ir_sequence_data.xml',
        'views/project_views.xml',
        'views/scaffold_views.xml',
        'views/account_move_views.xml',
        'views/account_analytic_line_views.xml',
        'views/sale_order_views.xml',
        'report/report_parte_unico.xml',
        'report/account_move_document.xml',
        'report/report_partial_part_document.xml',
        'wizard/scaffold_partial_report_wizard_views.xml',
        'wizard/create_account_analytic_line_wizard_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            '/andamios_extend/static/src/js/list_controller.js',
            '/andamios_extend/static/src/xml/list_view_buttons.xml',
        ],
    },
}
