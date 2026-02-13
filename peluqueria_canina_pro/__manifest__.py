# -*- coding: utf-8 -*-
{
    'name': "Peluquería Canina PRO",
    'summary': "Gestión Profesional de Peluquería Canina con Centro de Costos",
    'description': """
        Módulo PRO para gestión completa de peluquería canina:
        ========================================================
        
        * 📋 Catálogo de Servicios con precios
        * 📅 Sistema de Turnos mejorado con estados
        * 📝 Historial completo de Visitas
        * 💰 Centro de Costos integrado
        * 📊 Dashboard con KPIs en tiempo real
        * 💵 Facturación automática
        * 📦 Control de productos y stock
        * 📈 Reportes financieros detallados
        
        Diseño responsive y moderno para cualquier dispositivo.
    """,
    'author': "Peluquería Canina",
    'website': "https://www.peluqueriacanina.com",
    'category': 'Services',
    'version': '19.0.1.0',
    'depends': [
        'peluqueria_canina',  # Módulo base
        'account',            # Facturación
        'product',            # Productos
        'stock',              # Inventario
        'calendar',           # Agenda
    ],
    'data': [
        # Seguridad
        'security/ir.model.access.csv',
        
        # Datos maestros
        'data/servicio_data.xml',
        
        # Vistas
        'views/dashboard_views.xml',
        'views/servicio_views.xml',
        'views/turno_views.xml',
        'views/visita_views.xml',
        'views/mascota_views.xml',
        'views/menu_views.xml',
        
        # Reportes
        'reports/reporte_financiero.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'icon': '/peluqueria_canina_pro/static/description/icon.png',
    'assets': {
        'web.assets_backend': [
            'peluqueria_canina_pro/static/src/css/dashboard.css',
        ],
    },
}
