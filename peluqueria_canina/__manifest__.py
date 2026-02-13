# -*- coding: utf-8 -*-
{
    'name': "Peluquería Canina",

    'summary': "Gestión de Peluquería Canina - Mascotas, Clientes y Turnos",

    'description': """
        Módulo para gestión integral de peluquería canina:
        - Registro de mascotas con información detallada
        - Gestión de clientes/dueños
        - Sistema de turnos con calendario
        - Historial de actividades
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Services',
    'version': '19.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/personas.xml',
        'views/mascotas.xml',
        'views/turno.xml',        
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'icon': '/peluqueria_canina/icon.png',  # Ruta al icono
}

