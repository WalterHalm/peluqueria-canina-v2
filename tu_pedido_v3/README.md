# Tu Pedido v3 - Sistema de Comidas Rápidas (Odoo 19)

## Descripción

Sistema completo de gestión de pedidos para restaurantes de comida rápida desarrollado para **Odoo 19 Community**. Permite gestionar pedidos desde el eCommerce y el módulo de ventas con un dashboard interactivo en tiempo real y sistema de notificaciones unificado.

## 🆕 Novedades en v3.0.0

### Migración a Odoo 19
- ✅ Actualizado para Odoo 19.0
- ✅ Assets de PoS actualizados: `point_of_sale.assets`
- ✅ Compatibilidad completa con OWL framework moderno
- ✅ Todas las rutas actualizadas a `/tu_pedido_v3/`
- ✅ Modelos y vistas actualizados

### Mejoras Técnicas
- Mejor rendimiento en dashboard
- Optimización de notificaciones en tiempo real
- Código más limpio y mantenible

## Características Principales

### 🎯 Dashboard Interactivo
- Vista Kanban con estados de pedidos: Nuevo → Aceptado → En Preparación → Terminado → Despachado/Retirado → Entregado → Rechazado
- Drag & Drop para cambiar estados de pedidos
- Actualización automática cada 30 segundos
- Notificaciones sonoras para pedidos nuevos (cada 10 segundos hasta aceptar/rechazar)
- Efectos visuales (parpadeo) para pedidos nuevos con desactivación automática
- **Filtros avanzados**:
  - 📅 Por fecha: Hoy (por defecto), Ayer, Últimos 7 días, Todos
  - 👤 Por cliente: Búsqueda por nombre
  - 🌐 Por origen: Web o Punto de Venta
  - 📊 Por estado: Todos los estados disponibles

### 🔔 Sistema de Notificaciones Unificado
- **🌐 Notificaciones Web**: Alertas de pedidos nuevos del eCommerce en PoS (botón azul)
- **🚚 Notificaciones Delivery**: Pedidos terminados listos para enviar (botón verde)
- **📍 Notificaciones Pickup**: Pedidos terminados listos para retirar (botón morado)
- Botones flotantes con contadores en tiempo real
- Modales informativos con acciones rápidas (Despachado/Entregado)
- Formateo inteligente de nombres de mesa ("TerrazaMesa5" → "Terraza Mesa 5")

### 📊 Información Detallada de Pedidos
- Nombre del cliente
- Productos con cantidades, unidades de medida y atributos
- Campo "Notas" para instrucciones de cocina
- Tiempo transcurrido por estado y tiempo total
- Botones de acción para cambiar estados

### 🛒 Integración con eCommerce
- API para verificar si el restaurante está abierto
- **Control de compras por sesión PoS**: Solo permite compras cuando hay sesión PoS abierta
- Banner de estado en carrito (abierto/cerrado)
- Página personalizada cuando el local está cerrado
- Creación automática de pedidos desde el eCommerce (solo al confirmar pago)
- **Página de confirmación mejorada** con seguimiento en tiempo real

### 📱 Confirmación del Cliente
- Botón "Recibí mi pedido" en página de confirmación
- Botón "Tengo un Problema" para generar reclamos
- Cambio automático a "Entregado" al confirmar recepción
- Interfaz amigable con emojis y colores intuitivos

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo 19
```bash
cp -r tu_pedido_v3 /path/to/odoo19/addons/
```

2. Reiniciar el servidor Odoo
```bash
./odoo-bin -c odoo.conf
```

3. Actualizar la lista de aplicaciones (Apps > Update Apps List)

4. Buscar "Tu Pedido v3" e instalar el módulo

## Compatibilidad

- **Odoo Version**: 19.0 Community
- **Dependencias**: sale, website_sale, portal, point_of_sale, pos_restaurant, pos_sale
- **Navegadores**: Chrome, Firefox, Safari, Edge (con soporte para Web Audio API)
- **Dispositivos**: Desktop, Tablet (responsive design)

## APIs Disponibles

### APIs eCommerce
- `/tu_pedido_v3/estado_restaurante` - Verifica si el restaurante está abierto
- `/tu_pedido_v3/estado_pedido/<order_id>` - Consulta el estado de un pedido
- `/tu_pedido_v3/confirmar_recepcion/<order_id>` - Cliente confirma recepción
- `/tu_pedido_v3/generar_reclamo/<order_id>` - Genera un reclamo

### APIs Dashboard
- `/tu_pedido_v3/dashboard_data` - Obtiene datos del dashboard
- `/tu_pedido_v3/cambiar_estado` - Cambia estado de pedido
- `/tu_pedido_v3/siguiente_estado` - Avanza al siguiente estado
- `/tu_pedido_v3/aceptar_pedido` - Acepta un pedido
- `/tu_pedido_v3/rechazar_pedido` - Rechaza un pedido

### APIs Notificaciones PoS
- `/tu_pedido_v3/pos_delivery_notifications` - Pedidos delivery terminados
- `/tu_pedido_v3/pos_pickup_notifications` - Pedidos pickup terminados
- `/tu_pedido_v3/pos_web_notifications` - Pedidos web nuevos
- `/tu_pedido_v3/mark_delivery_dispatched` - Marca como despachado

### APIs PoS
- `/tu_pedido_v3/crear_pedido_simple` - Crea pedido desde PoS

## Estados del Pedido

1. **Nuevo**: Pedido recién creado, esperando aceptación/rechazo
2. **Aceptado**: Pedido confirmado por el restaurante
3. **En Preparación**: Pedido en proceso de preparación
4. **Terminado**: Pedido listo para despacho
5. **Despachado/Retirado**: Pedido entregado al cliente o listo para retiro
6. **Entregado**: Cliente confirmó recepción del pedido
7. **Rechazado**: Pedido rechazado por el restaurante

## Migración desde v2

Si estás migrando desde Tu Pedido v2 (Odoo 18):

1. **Backup**: Haz backup completo de tu base de datos
2. **Desinstalar v2**: Desinstala el módulo tu_pedido_v2
3. **Instalar v3**: Instala tu_pedido_v3
4. **Datos**: Los datos de pedidos se mantienen (mismo modelo sale.order)

## Soporte

- **Repositorio**: https://github.com/WalterHalm/tu_pedido_v3
- **Issues**: Reportar problemas en GitHub
- **Versión anterior**: Para Odoo 18, usar tu_pedido_v2

## Licencia

LGPL-3

---

**Versión**: 3.0.0  
**Última actualización**: Enero 2025  
**Autor**: Walter Halm - Tu Pedido v3  
**Compatible con**: Odoo 19.0 Community

---

## Changelog v3.0.0

### ✨ Migración a Odoo 19
- Actualizado para Odoo 19.0 Community
- Assets de PoS: `point_of_sale._assets_pos` → `point_of_sale.assets`
- Todas las rutas actualizadas de v2 a v3
- Modelos y wizards actualizados
- Vistas XML compatibles con Odoo 19

### 🔧 Mejoras Técnicas
- Mejor compatibilidad con OWL framework
- Optimización de código JavaScript
- Limpieza de dependencias obsoletas
- Mejoras en rendimiento del dashboard

### 📝 Documentación
- README actualizado para Odoo 19
- Guía de migración desde v2
- APIs documentadas con nuevas rutas
