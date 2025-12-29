{
    'name': "google map scaffold",

    'summary': """
        This addon add link to web_google_map.
        """,
    'author': "Binhex",
    'website': "https://github.com/BinhexTeam/ateca_custom",

    'category': 'Custom',
    'version': "18.0.1.0.0",
    'license' : 'AGPL-3',

    'depends': [
        'web_view_google_map',
        'andamios_extend',
        'web_view_google_maps_drag',
    ],

    'data': [
        'views/scaffold_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'google_map_scaffold/static/src/views/google_map/google_map_arch_parser.js',
            'google_map_scaffold/static/src/views/google_map/google_map_controller.js',
            'google_map_scaffold/static/src/views/google_map/google_map_renderer.js',
            'google_map_scaffold/static/src/views/google_map/google_map_renderer.xml',
            'google_map_scaffold/static/src/views/google_map/google_map_view.js',
        ],
    },
}
