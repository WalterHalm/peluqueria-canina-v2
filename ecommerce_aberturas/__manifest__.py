{
    'name': 'E-commerce Ventanas PVC',
    'version': '19.0.2.0.0',
    'category': 'Sales/E-commerce',
    'summary': 'Tienda online profesional para venta de ventanas PVC',
    'description': """
        E-commerce Ventanas PVC Profesional
        ====================================
        - Catálogo por series con fichas técnicas
        - Carrito completo con impuestos y envíos
        - Testimonios de clientes
        - Seguimiento de pedidos
        - Precios diferenciados particulares/distribuidores
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website',
        'website_sale',
        'sale_management',
        'stock',
        'delivery',
        'payment',
        'portal',
        'rating',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_pvc_window_views.xml',
        'views/customer_testimonial_views.xml',
        'views/sale_order_views.xml',
        'views/menu_views.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ecommerce_aberturas/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
