# DOCUMENTO DE DESARROLLO - Tu Pedido v3

## Información General

**Proyecto**: Tu Pedido v3 - Sistema de Gestión de Pedidos para Restaurantes  
**Versión**: 3.0.0  
**Plataforma**: Odoo 19.0 Community  
**Autor**: Walter Halm  
**Fecha Inicio**: Enero 2025  
**Estado**: En Desarrollo - Migración desde v2 completada

---

## 1. ARQUITECTURA DEL SISTEMA

### 1.1 Estructura de Módulos

```
tu_pedido_v3/
├── controllers/          # Controladores HTTP (API REST)
├── models/              # Modelos de datos (ORM)
├── wizards/             # Wizards transitorios
├── views/               # Vistas XML (UI)
├── security/            # Permisos y accesos
└── static/
    └── src/
        ├── js/          # JavaScript (OWL)
        ├── css/         # Estilos
        └── xml/         # Templates OWL
```

### 1.2 Dependencias

```python
'depends': [
    'base',              # Core Odoo
    'sale',              # Órdenes de venta
    'website_sale',      # eCommerce
    'portal',            # Portal clientes
    'point_of_sale',     # PoS
    'pos_restaurant',    # PoS Restaurante
    'pos_sale',          # Integración PoS-Sale
]
```

---

## 2. MODELOS DE DATOS

### 2.1 sale.order (Extensión)

**Archivo**: `models/sale_order.py`

**Campos Agregados**:
```python
estado_rapido = Selection([...])           # Estado del pedido
nota_cocina = Text()                       # Notas para cocina
tiempo_inicio_estado = Datetime()          # Timestamp estado actual
tiempo_inicio_total = Datetime()           # Timestamp creación
sonido_activo = Boolean()                  # Control notificaciones
es_para_envio = Boolean()                  # Delivery vs Pickup
direccion_entrega_completa = Text()        # Dirección formateada
cliente_confirmo_recepcion = Boolean()     # Confirmación cliente
tiempo_estimado_entrega = Integer()        # Minutos estimados
tiene_reclamo = Boolean()                  # Flag reclamo
descripcion_reclamo = Text()               # Descripción reclamo
productos_modificados = Boolean()          # Flag modificación
tiempo_estado_minutos = Integer(compute)   # Minutos en estado
tiempo_total_minutos = Integer(compute)    # Minutos totales
```

**Métodos Principales**:
- `create()`: Activa pedidos web automáticamente
- `action_cambiar_estado()`: Cambia estado y actualiza timestamps
- `action_siguiente_estado()`: Avanza al siguiente estado
- `action_confirmar_recepcion_cliente()`: Cliente confirma entrega
- `_format_address()`: Formatea dirección de entrega

**Lógica de Negocio**:
1. Pedidos web se crean con `estado_rapido='nuevo'` y `sonido_activo=True`
2. Detecta automáticamente si es delivery por `partner_shipping_id`
3. Al cambiar a 'terminado' confirma la orden automáticamente
4. Al rechazar cancela la orden automáticamente

### 2.2 pos.order (Extensión)

**Archivo**: `models/pos_order.py`

**Campos Agregados**:
```python
estado_rapido = Selection([...])
is_delivery = Boolean()
direccion_delivery = Char()
telefono_delivery = Char()
enviado_a_cocina = Boolean()
tiempo_inicio_estado = Datetime()
tiempo_inicio_total = Datetime()
sonido_activo = Boolean()
tiempo_estado_minutos = Integer(compute)
tiempo_total_minutos = Integer(compute)
```

### 2.3 pos.session (Extensión)

**Archivo**: `models/pos_session.py`

**Campos Agregados**:
```python
fecha_apertura = Datetime(default=now)
hora_cierre_estimada = Float(default=22.0)
```

**Uso**: Control de apertura/cierre del restaurante

### 2.4 payment.transaction (Extensión)

**Archivo**: `models/payment_transaction.py`

**Propósito**: Hook para activar pedidos después del pago

---

## 3. CONTROLADORES (API REST)

### 3.1 Dashboard Controller

**Archivo**: `controllers/dashboard_controller.py`

**Rutas**:
```python
GET  /tu_pedido_v3/dashboard              # Vista dashboard
POST /tu_pedido_v3/dashboard_data         # Obtener datos
POST /tu_pedido_v3/cambiar_estado         # Cambiar estado
POST /tu_pedido_v3/siguiente_estado       # Siguiente estado
POST /tu_pedido_v3/aceptar_pedido         # Aceptar pedido
POST /tu_pedido_v3/rechazar_pedido        # Rechazar pedido
POST /tu_pedido_v3/toggle_producto        # Toggle producto
```

**Respuesta dashboard_data**:
```json
{
  "columns": [
    {
      "key": "nuevo",
      "title": "🆕 Nuevo",
      "orders": [...],
      "count": 5
    }
  ]
}
```

### 3.2 eCommerce Controller

**Archivo**: `controllers/ecommerce_controller.py`

**Rutas**:
```python
POST /tu_pedido_v3/estado_restaurante     # Estado abierto/cerrado
POST /tu_pedido_v3/estado_pedido/<id>     # Estado de pedido
POST /tu_pedido_v3/confirmar_recepcion/<id> # Cliente confirma
POST /tu_pedido_v3/generar_reclamo/<id>   # Generar reclamo
```

### 3.3 PoS Notifications Controller

**Archivo**: `controllers/pos_notifications.py`

**Rutas**:
```python
POST /tu_pedido_v3/pos_delivery_notifications  # Delivery listos
POST /tu_pedido_v3/pos_pickup_notifications    # Pickup listos
POST /tu_pedido_v3/pos_web_notifications       # Web nuevos
POST /tu_pedido_v3/mark_delivery_dispatched    # Marcar despachado
```

**Lógica**:
- Formatea nombres de mesa: "TerrazaMesa5" → "Terraza Mesa 5"
- Detecta tipo de pedido (pos/web)
- Retorna notificaciones activas

### 3.4 PoS Simple Controller

**Archivo**: `controllers/pos_simple_controller.py`

**Rutas**:
```python
POST /tu_pedido_v3/crear_pedido_simple    # Crear desde PoS
```

**Funcionalidad**:
- Crea pedidos desde PoS al dashboard
- Maneja combos y atributos
- Detecta delivery por productos
- Actualiza pedidos existentes
- Tracking por `tracking_number`

### 3.5 Shop Status Controller

**Archivo**: `controllers/shop_status_controller.py`

**Rutas**:
```python
POST /shop/status                          # Estado sesión PoS
GET  /shop/cart                            # Carrito con estado
```

---

## 4. FRONTEND (OWL + JavaScript)

### 4.1 Dashboard Component

**Archivo**: `static/src/js/dashboard.js`  
**Template**: `static/src/xml/dashboard_template.xml`

**Tecnología**: OWL Framework (Odoo 19)

**Estado del Componente**:
```javascript
state = {
  state_columns: [],      // Columnas filtradas
  all_columns: [],        // Todas las columnas
  loading: false,
  error: null,
  showAceptarModal: false,
  showRechazarModal: false,
  filters: {
    fecha: 'hoy',
    cliente: '',
    origen: 'todos',
    estado: 'todos'
  },
  modalData: {...}
}
```

**Funcionalidades**:
1. **Drag & Drop**: Cambiar estado arrastrando tarjetas
2. **Auto-refresh**: Cada 30 segundos
3. **Notificaciones sonoras**: Cada 10 segundos para nuevos
4. **Filtros avanzados**: Fecha, cliente, origen, estado
5. **Timers en tiempo real**: Actualización cada segundo
6. **Modales**: Aceptar, rechazar, cambios, cancelación

**Ciclo de Vida**:
```javascript
onWillStart()  → loadData()
onMounted()    → setupDragAndDrop(), startAutoRefresh(), initAudio()
onWillUnmount() → clearIntervals()
```

### 4.2 PoS Kitchen Simple

**Archivo**: `static/src/js/pos_kitchen_simple.js`

**Patch**: `ActionpadWidget.prototype`

**Funcionalidad**:
- Botón "Enviar a Cocina" en PoS
- Envía pedidos al dashboard
- Maneja combos y notas
- Detecta mesa y tracking_number

### 4.3 PoS Delivery Notifications

**Archivo**: `static/src/js/pos_delivery_notifications_pos.js`

**Clase**: `PosDeliveryNotifications`

**Sistema de Notificaciones**:
1. **Delivery** (Verde): Pedidos listos para enviar
2. **Pickup** (Morado): Pedidos listos para retirar
3. **Web** (Azul): Pedidos web nuevos

**Intervalos**:
- Verificación: Cada 15 segundos
- Primera verificación: 3 segundos después de iniciar

**Botones Flotantes**:
```javascript
.pos-delivery-float-btn   // Verde
.pos-pickup-float-btn     // Morado
.pos-web-float-btn        // Azul
```

---

## 5. VISTAS XML

### 5.1 Dashboard Action

**Archivo**: `views/dashboard_action.xml`

```xml
<record id="action_pedido_dashboard" model="ir.actions.client">
  <field name="name">Dashboard de Pedidos - Tu Pedido v3</field>
  <field name="tag">pedido_dashboard</field>
  <field name="target">fullscreen</field>
</record>
```

### 5.2 Wizards

**Archivo**: `views/wizard_views.xml`

**Modelos**:
- `tu_pedido_v3.aceptar_pedido_wizard`
- `tu_pedido_v3.rechazar_pedido_wizard`

### 5.3 Shop Views

**Archivos**:
- `shop_confirmation.xml`: Página confirmación pedido
- `shop_cart_status.xml`: Banner estado en carrito
- `shop_closed.xml`: Página local cerrado

---

## 6. SEGURIDAD

**Archivo**: `security/ir.model.access.csv`

**Permisos**:
```csv
model_tu_pedido_v3_aceptar_pedido_wizard,base.group_user,1,1,1,1
model_tu_pedido_v3_rechazar_pedido_wizard,base.group_user,1,1,1,1
```

---

## 7. ASSETS (Odoo 19)

### 7.1 Backend Assets

```python
'web.assets_backend': [
    'tu_pedido_v3/static/src/css/dashboard.css',
    'tu_pedido_v3/static/src/js/dashboard.js',
    'tu_pedido_v3/static/src/xml/dashboard_template.xml',
]
```

### 7.2 PoS Assets (CRÍTICO PARA ODOO 19)

```python
'point_of_sale.assets': [  # NO _assets_pos
    'tu_pedido_v3/static/src/js/pos_kitchen_simple.js',
    'tu_pedido_v3/static/src/xml/pos_kitchen_simple.xml',
    'tu_pedido_v3/static/src/css/pos_kitchen_simple.css',
    'tu_pedido_v3/static/src/js/pos_delivery_notifications_pos.js',
    'tu_pedido_v3/static/src/css/pos_delivery_notifications_pos.css',
]
```

**IMPORTANTE**: En Odoo 19 cambió de `point_of_sale._assets_pos` a `point_of_sale.assets`

---

## 8. FLUJO DE DATOS

### 8.1 Pedido Web (eCommerce)

```
1. Cliente crea pedido → sale.order (draft)
2. Cliente paga → payment.transaction
3. Pago confirmado → sale.order.create() activa pedido
4. estado_rapido = 'nuevo', sonido_activo = True
5. Dashboard muestra pedido con sonido
6. PoS recibe notificación web (azul)
7. Restaurante acepta → estado = 'aceptado'
8. Preparación → estado = 'en_preparacion'
9. Listo → estado = 'terminado'
10. Sistema detecta es_para_envio
11. PoS recibe notificación delivery/pickup
12. Despacho → estado = 'despachado'
13. Cliente confirma → estado = 'entregado'
```

### 8.2 Pedido PoS

```
1. Mesero crea pedido en PoS
2. Click "Enviar a Cocina"
3. POST /tu_pedido_v3/crear_pedido_simple
4. Crea sale.order con estado_rapido='nuevo'
5. Dashboard muestra pedido
6. Flujo continúa igual que web
```

---

## 9. ESTADOS DEL PEDIDO

```
nuevo → aceptado → en_preparacion → terminado → despachado → entregado
                                              ↓
                                          rechazado
```

**Transiciones Automáticas**:
- `terminado` → Confirma orden de venta
- `rechazado` → Cancela orden de venta
- `nuevo` → `aceptado/rechazado` → Desactiva sonido

---

## 10. NOTIFICACIONES

### 10.1 Dashboard
- **Sonoras**: Cada 10s para pedidos nuevos
- **Visuales**: Parpadeo en tarjetas nuevas
- **Auto-desactivación**: Al aceptar/rechazar

### 10.2 PoS
- **Verificación**: Cada 15s
- **Tipos**: Web (azul), Delivery (verde), Pickup (morado)
- **Persistencia**: Hasta marcar como despachado

---

## 11. FILTROS AVANZADOS

**Implementación**: `dashboard.js → applyFilters()`

**Filtros**:
1. **Fecha**: Hoy (default), Ayer, Últimos 7 días, Todos
2. **Cliente**: Búsqueda por nombre (case-insensitive)
3. **Origen**: Web, PoS, Todos
4. **Estado**: Cualquier estado del pedido

**Lógica**:
- Filtros se aplican sobre `all_columns`
- Resultado en `state_columns`
- Actualización en tiempo real

---

## 12. TIMERS EN TIEMPO REAL

**Implementación**: `dashboard.js → updateTimeCounters()`

**Funcionamiento**:
```javascript
// Cada segundo
tiempo_total = tiempo_inicial + (Date.now() - inicio) / 60000

// Colores
< 30 min: normal (verde)
30-60 min: advertencia (amarillo)
> 60 min: crítico (rojo)
```

---

## 13. DRAG & DROP

**Implementación**: HTML5 Drag & Drop API

**Eventos**:
```javascript
dragstart  → Guarda order_id
dragover   → Permite drop
drop       → Cambia estado
dragleave  → Limpia estilos
dragend    → Limpia clases
```

**Restricciones**: Ninguna, cualquier estado puede moverse a cualquier otro

---

## 14. COMPATIBILIDAD ODOO 19

### 14.1 Cambios Críticos

**Assets PoS**:
```python
# Odoo 18
'point_of_sale._assets_pos': [...]

# Odoo 19
'point_of_sale.assets': [...]
```

**Método create()**:
```python
# Siempre recibe lista en Odoo 19
def create(self, vals_list):
    if not isinstance(vals_list, list):
        vals_list = [vals_list]
```

**OWL Framework**:
- ✅ Compatible sin cambios
- ✅ Imports desde `@odoo/owl`
- ✅ Registry desde `@web/core/registry`

### 14.2 Sin Cambios Necesarios

- ✅ Controladores HTTP
- ✅ Vistas XML
- ✅ Modelos Python (excepto create)
- ✅ Templates OWL
- ✅ CSS

---

## 15. TESTING

### 15.1 Tests Manuales Requeridos

**Backend**:
- [ ] Crear pedido web → Verificar estado_rapido
- [ ] Crear pedido PoS → Verificar en dashboard
- [ ] Cambiar estados → Verificar timestamps
- [ ] Confirmar orden → Verificar en terminado
- [ ] Rechazar orden → Verificar cancelación

**Frontend**:
- [ ] Dashboard carga correctamente
- [ ] Drag & drop funciona
- [ ] Filtros funcionan
- [ ] Modales abren/cierran
- [ ] Sonidos reproducen
- [ ] Timers actualizan

**PoS**:
- [ ] Botón "Enviar a Cocina" visible
- [ ] Pedido llega al dashboard
- [ ] Notificaciones aparecen
- [ ] Botones flotantes funcionan
- [ ] Modales muestran info correcta

**eCommerce**:
- [ ] Banner estado en carrito
- [ ] Página cerrado funciona
- [ ] Confirmación muestra pedido
- [ ] Cliente puede confirmar recepción

### 15.2 Tests Unitarios (Pendiente)

```python
# tests/test_sale_order.py
def test_create_web_order()
def test_change_state()
def test_auto_confirm()
def test_auto_cancel()
```

---

## 16. PROBLEMAS CONOCIDOS

### 16.1 Resueltos

✅ Assets PoS no cargaban → Cambio a `point_of_sale.assets`  
✅ Rutas 404 → Actualización de v2 a v3  
✅ Templates no encontrados → Actualización nombres  
✅ dashboard.js faltante → Copiado y actualizado

### 16.2 Pendientes

⚠️ Tests unitarios no implementados  
⚠️ Documentación API incompleta  
⚠️ Logs de debug en producción

---

## 17. ROADMAP

### v3.1.0 (Próxima)
- [ ] Tests unitarios completos
- [ ] Logs configurables
- [ ] Métricas y analytics
- [ ] Reportes PDF

### v3.2.0 (Futuro)
- [ ] Multi-idioma (i18n)
- [ ] Notificaciones push
- [ ] App móvil
- [ ] Integración WhatsApp

---

## 18. NOTAS PARA DESARROLLADORES

### 18.1 Convenciones de Código

**Python**:
- PEP 8
- Docstrings en métodos públicos
- Type hints recomendados

**JavaScript**:
- ES6+
- Async/await preferido
- Comentarios en funciones complejas

**XML**:
- Indentación 2 espacios
- IDs descriptivos
- Comentarios en secciones

### 18.2 Git Workflow

```bash
# Feature branch
git checkout -b feature/nueva-funcionalidad

# Commits descriptivos
git commit -m "feat: agregar filtro por mesa"

# Pull request
git push origin feature/nueva-funcionalidad
```

### 18.3 Debugging

**Backend**:
```python
import logging
_logger = logging.getLogger(__name__)
_logger.info("Debug message")
```

**Frontend**:
```javascript
console.log("Debug:", data);
```

**PoS**:
```javascript
console.log("DEBUG:", message);
```

---

## 19. CONTACTO Y SOPORTE

**Autor**: Walter Halm  
**Email**: [pendiente]  
**GitHub**: https://github.com/WalterHalm/tu_pedido_v3  
**Issues**: Reportar en GitHub

---

**Última actualización**: Enero 2025  
**Versión documento**: 1.0  
**Estado**: Completo
