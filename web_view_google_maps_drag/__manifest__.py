{
    'name': 'Web View Google Maps Drag',
    'version': '18.0.1.0',
    'description': 'A module to add drag functionality to Google Maps in Odoo views.',
    'author': 'Comunitea',
    'website': 'www.comunitea.com',
    'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': 'Enhances Google Maps view with drag functionality',
    'depends': [
        'web_view_google_map',
    ],
    'data': [],
    'auto_install': False,
    'application': False,
    'assets': {
         'web.assets_backend': [
            'web_view_google_maps_drag/static/src/js/*',
        ],
    }
}