# Peluquería Canina - Módulo Odoo 19

Módulo de gestión integral para peluquerías caninas.

## Características

- **Gestión de Mascotas**: Registro completo con foto, datos físicos y comportamiento
- **Gestión de Clientes**: Vinculación con contactos de Odoo
- **Historial**: Seguimiento de actividades mediante mail.thread
- **Turnos**: Programación de próximas visitas

## Instalación

1. Copiar módulo a `addons_extras/`
2. Actualizar lista de aplicaciones en Odoo
3. Instalar "Peluquería Canina"

## Uso

- **Menú Principal**: Peluqueria Patitas
  - Mascotas: Vista kanban, lista y formulario
  - Personas: Clientes con sus mascotas

## Migración desde Odoo 17

Ver `migration/README.md` y `GUIA_MIGRACION_RAPIDA.md` para instrucciones detalladas.

**Scripts disponibles:**
- `migration/validar_pre_migracion.py` - Validación de datos
- `migration/migracion_definitiva.py` - Migración completa
- `migration/limpiar_datos.py` - Limpieza de pruebas

## Estructura

```
peluqueria_canina/
├── models/          # Modelos de datos
├── views/           # Vistas XML
├── security/        # Permisos
└── static/          # Recursos estáticos
```

## Versión

- **Odoo**: 19.0
- **Módulo**: 19.0.0.1
- **Licencia**: LGPL-3

## Soporte

Desarrollado para gestión de peluquerías caninas en Argentina.
