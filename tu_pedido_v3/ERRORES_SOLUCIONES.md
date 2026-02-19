# ERRORES Y SOLUCIONES - Tu Pedido v3

## Error #1: External ID not found - action_pedido_dashboard

**Fecha**: 14/02/2026  
**Estado**: ✅ RESUELTO

### Descripción del Error

```
ValueError: External ID not found in the system: tu_pedido_v3.action_pedido_dashboard

while parsing file:/c:/program%20files/odoo%2019.0.20251002/server/odoo/addons_extras/tu_pedido_v3/views/menu_views.xml:8
```

### Causa

El archivo `menu_views.xml` estaba referenciando el action sin el prefijo del módulo:

```xml
<!-- INCORRECTO -->
<menuitem id="menu_tu_pedido_main"
          name="Tu Pedido"
          action="action_pedido_dashboard"
          web_icon="tu_pedido_v2,static/description/icon2.png"
          sequence="50"/>
```

Además, el `web_icon` todavía tenía la referencia a `tu_pedido_v2`.

### Solución

Actualizar `views/menu_views.xml` con las referencias correctas:

```xml
<!-- CORRECTO -->
<menuitem id="menu_tu_pedido_main"
          name="Tu Pedido"
          action="tu_pedido_v3.action_pedido_dashboard"
          web_icon="tu_pedido_v3,static/description/icon2.png"
          sequence="50"/>
```

### Cambios Realizados

1. ✅ `action="action_pedido_dashboard"` → `action="tu_pedido_v3.action_pedido_dashboard"`
2. ✅ `web_icon="tu_pedido_v2,..."` → `web_icon="tu_pedido_v3,..."`

### Archivos Modificados

- `views/menu_views.xml`

### Verificación

```bash
# Reintentar instalación
Apps → Update Apps List → Buscar "Tu Pedido v3" → Install
```

---

## Lecciones Aprendidas

### 1. Referencias de Actions en Odoo

En Odoo, cuando se referencia un action desde un menuitem, se debe usar el formato completo:

```xml
<!-- Formato correcto -->
action="nombre_modulo.id_del_action"

<!-- NO usar -->
action="id_del_action"
```

### 2. Referencias de Assets (web_icon)

Los assets estáticos también deben referenciar el módulo correcto:

```xml
<!-- Formato correcto -->
web_icon="nombre_modulo,ruta/al/archivo"

<!-- NO usar -->
web_icon="modulo_antiguo,ruta/al/archivo"
```

### 3. Checklist de Migración

Al migrar de v2 a v3, verificar:

- [ ] Nombres de modelos (`tu_pedido_v2.*` → `tu_pedido_v3.*`)
- [ ] Referencias de actions con prefijo de módulo
- [ ] Referencias de assets (web_icon, etc.)
- [ ] Rutas de API (`/tu_pedido_v2/` → `/tu_pedido_v3/`)
- [ ] Templates OWL
- [ ] Registry de JavaScript

---

## Estado Actual

**Módulo**: ✅ LISTO PARA INSTALAR  
**Errores Conocidos**: 0  
**Advertencias**: 0 críticas

---

**Última actualización**: 14/02/2026  
**Próximo paso**: Instalar módulo en Odoo 19
