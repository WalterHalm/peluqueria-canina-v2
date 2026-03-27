{
    'name': 'Real Estate',
    'version': '19.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Gestión de propiedades en alquiler y venta con mapa, iCal y captación',
    'depends': [
        'website',
        'website_sale',
        'sale_renting',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ical_cron.xml',
        'views/res_config_settings_views.xml',
        'views/product_template_views.xml',
        'views/property_submission_views.xml',
        'views/ical_sync_views.xml',
        'views/menus.xml',
        'templates/whatsapp_social.xml',
        'templates/map_page.xml',
        'templates/product_map.xml',
        'templates/captacion.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'real_estate/static/src/css/floating_buttons.css',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
