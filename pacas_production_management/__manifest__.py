{
    'name': 'Pacas Production Management',
    'version': '19.0.2.0.0',
    'category': 'Supply Chain/Manufacturing',
    'summary': 'Gestión de producción de pacas de ropa clasificada desde contenedores',
    'description': """
        Capa operativa sobre Odoo nativo para controlar la recepción de
        contenedores de ropa usada, clasificación rápida por categoría/calidad,
        y generación automática de órdenes de fabricación.
        
        Todo el proceso de manufactura, inventario, compras y ventas
        se maneja con los módulos estándar de Odoo.
    """,
    'depends': ['mrp', 'purchase', 'sale_management', 'stock', 'contacts'],
    'data': [
        'security/pacas_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/pacas_container_views.xml',
        'views/pacas_classification_views.xml',
        'views/inherited_views.xml',
        'views/pacas_menus.xml',
        'report/pacas_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
