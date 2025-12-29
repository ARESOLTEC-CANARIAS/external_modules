{
    'name': "Binhex Andamios Informes",

    'summary': """
        Generación de reportes de ventas y tareas referido a Andamios""",

    'description': """
        Módulo que añade varios campos a los modelos de Tarea y Ventas con el objetivo de generar informes de Parte de trabajo y varios tipos de Presupuesto
        """,

    'author': "Binhex Systems Solution S.L.",
    'website': "http://binhex.es",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': "18.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'web', 'binhex_andamios', 'project_task_material'],

    # always loaded
    'data': [
        'report/report_andamio.xml',
        'report/report_informe_andamio.xml',
        'report/report_parte_trabajo_andamio.xml',
        'report/report_parte_unico.xml',
        'report/report_saleorder_document.xml',
        'report/report_saleorder_generic.xml',
        'report/report_saleorder_specific.xml',
        'report/sale_report_presupuesto.xml',
        'report/task_report.xml',
        'report/task_report_action.xml',
        'report/external_layout_standard.xml',
        # 'report/andamios_styles.xml',
        'views/sale.xml',
        'views/task.xml',
        'views/sign_task_portal.xml',
    ],

    'assets': {
        'web.report_assets_common': [
            'binhex_andamios_report/static/src/css/andamios.scss',
        ],
    },
}
