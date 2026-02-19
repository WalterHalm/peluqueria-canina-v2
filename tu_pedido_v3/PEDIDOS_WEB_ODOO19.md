# Pedidos Web - Migración Odoo 19

## ✅ CAMBIOS IMPLEMENTADOS

### 1. **payment_transaction.py**
- ✅ Implementado `_post_process()` para interceptar pagos confirmados
- ✅ Activa `estado_rapido='nuevo'` cuando pago online se confirma
- ✅ Compatible con todos los métodos de pago online de Odoo 19

### 2. **sale_order.py**
- ✅ Implementado `action_confirm()` para interceptar confirmación de pedidos
- ✅ Detecta métodos de pago `cash_on_delivery` y `pay_on_site` (custom_mode)
- ✅ Activa dashboard para estos métodos al confirmar pedido
- ✅ Implementado `_detectar_tipo_entrega()`:
  - Detecta `carrier_id.delivery_type == 'in_store'` → pickup
  - Detecta `carrier_id.delivery_type in ['fixed', 'base_on_rule']` → delivery
  - Detecta productos con keywords de envío/recolección
  - Captura dirección completa para delivery
- ✅ Implementado `_crear_snapshot_productos()` para tracking de cambios
- ✅ Estado unificado: `'preparacion'` (no `'en_preparacion'`)

### 3. **pos_session.py**
- ✅ Implementado `get_info_sesion_abierta()` para verificar estado

### 4. **shop_status_controller.py**
- ✅ Actualizado para usar `get_info_sesion_abierta()`
- ✅ Retorna info completa de sesión PoS

### 5. **Vistas XML**
- ✅ `shop_confirmation.xml`: Rutas actualizadas a `/tu_pedido_v3/`
- ✅ `portal_integration.xml`: Rutas actualizadas a `/tu_pedido_v3/`
- ✅ Estados corregidos en progreso bars

### 6. **ecommerce_controller.py**
- ✅ Estados unificados: `'preparacion'` en lugar de `'en_preparacion'`

## 🔄 FLUJO COMPLETO DE PEDIDOS WEB

### A. **Pago Online (Tarjeta, PayPal, etc.)**
```
1. Cliente realiza pedido → sale.order creado en draft
2. Cliente paga → payment.transaction creado
3. Pago confirmado → payment.transaction._post_process()
4. Se activa: estado_rapido='nuevo', sonido_activo=True
5. Se ejecuta: _detectar_tipo_entrega()
6. Pedido aparece en dashboard con sonido
```

### B. **Cash on Delivery (Pago contra entrega)**
```
1. Cliente realiza pedido → sale.order creado en draft
2. Cliente selecciona "Cash on Delivery"
3. Pedido se confirma → sale.order.action_confirm()
4. Se detecta: provider.custom_mode == 'cash_on_delivery'
5. Se activa: estado_rapido='nuevo', sonido_activo=True
6. Se ejecuta: _detectar_tipo_entrega()
7. Pedido aparece en dashboard con sonido
```

### C. **Pay on Site (Pago en sitio)**
```
1. Cliente realiza pedido → sale.order creado en draft
2. Cliente selecciona "Pay on Site"
3. Pedido se confirma → sale.order.action_confirm()
4. Se detecta: provider.custom_mode == 'on_site'
5. Se activa: estado_rapido='nuevo', sonido_activo=True
6. Se ejecuta: _detectar_tipo_entrega()
7. Pedido aparece en dashboard con sonido
```

## 📦 DETECCIÓN DE TIPO DE ENTREGA

### Delivery (es_para_envio=True)
- `carrier_id.delivery_type in ['fixed', 'base_on_rule']`
- Productos con: "envío", "envio", "delivery", "shipping", "entrega"
- Captura dirección completa del partner_shipping_id

### Pickup (es_para_envio=False)
- `carrier_id.delivery_type == 'in_store'`
- Productos con: "recolección", "recoleccion", "retiro", "pickup"
- No captura dirección

## 🎯 MÉTODOS DE PAGO SOPORTADOS

### Online (via _post_process)
- Tarjetas de crédito/débito
- PayPal
- Stripe
- Mercado Pago
- Cualquier payment provider online

### Offline (via action_confirm)
- Cash on Delivery (`custom_mode='cash_on_delivery'`)
- Pay on Site (`custom_mode='on_site'`)

## 📊 ESTADOS DEL PEDIDO

Estados unificados en todo el módulo:
1. `nuevo` - Pedido recibido
2. `aceptado` - Confirmado por restaurante
3. `preparacion` - En preparación (NO "en_preparacion")
4. `terminado` - Listo para despacho
5. `despachado` - Despachado/Retirado
6. `entregado` - Cliente confirmó recepción
7. `rechazado` - Rechazado por restaurante

## 🔧 CONFIGURACIÓN REQUERIDA

### 1. Métodos de Pago
Instalar módulo: `website_sale_collect`
- Activa automáticamente "Pay on Site"
- Configura "Cash on Delivery" en Delivery Methods

### 2. Métodos de Entrega
- **Envío estándar**: Crear delivery carrier con `delivery_type='fixed'`
- **Recolección en tienda**: Crear con `delivery_type='in_store'`

### 3. Sesión PoS
- Debe haber sesión PoS abierta para permitir compras web
- Banner en carrito muestra estado (abierto/cerrado)

## 🧪 TESTING

### Test 1: Pago Online
1. Abrir sesión PoS
2. Ir a /shop
3. Agregar productos
4. Seleccionar "Envío estándar"
5. Pagar con tarjeta
6. Verificar que aparece en dashboard con sonido

### Test 2: Cash on Delivery
1. Abrir sesión PoS
2. Ir a /shop
3. Agregar productos
4. Seleccionar "Cash on Delivery"
5. Confirmar pedido
6. Verificar que aparece en dashboard con sonido

### Test 3: Pay on Site + Pickup
1. Abrir sesión PoS
2. Ir a /shop
3. Agregar productos
4. Seleccionar "Recolección en tienda"
5. Seleccionar "Pay on Site"
6. Confirmar pedido
7. Verificar que aparece en dashboard
8. Verificar que es_para_envio=False

### Test 4: Página de Confirmación
1. Realizar pedido
2. Ir a /shop/confirmation
3. Verificar barra de progreso
4. Verificar detalle de productos
5. Verificar información de entrega
6. Esperar 30 segundos → auto-refresh

### Test 5: Portal del Cliente
1. Realizar pedido
2. Ir a /my/orders
3. Abrir pedido
4. Verificar widget de estado
5. Cambiar estado en dashboard
6. Esperar 30 segundos → auto-refresh

## 🐛 TROUBLESHOOTING

### Pedido no aparece en dashboard
- ✅ Verificar que hay sesión PoS abierta
- ✅ Verificar que el pago se confirmó (payment.transaction.state='done')
- ✅ Verificar que es pedido web (order.website_id existe)
- ✅ Verificar logs en payment_transaction._post_process()

### Tipo de entrega incorrecto
- ✅ Verificar carrier_id.delivery_type
- ✅ Verificar nombres de productos
- ✅ Revisar método _detectar_tipo_entrega()

### Rutas no funcionan
- ✅ Verificar que todas las rutas usan `/tu_pedido_v3/`
- ✅ Reiniciar servidor Odoo
- ✅ Actualizar módulo

## 📝 NOTAS IMPORTANTES

1. **Estados**: Usar `'preparacion'` NO `'en_preparacion'`
2. **Rutas**: Todas deben ser `/tu_pedido_v3/`
3. **Sesión PoS**: Obligatoria para compras web
4. **Métodos de pago**: Detectar por `provider.custom_mode`
5. **Delivery type**: Usar `carrier_id.delivery_type`

## 🚀 PRÓXIMOS PASOS

1. ✅ Probar flujo completo en Odoo 19
2. ⏳ Verificar notificaciones PoS
3. ⏳ Probar con diferentes métodos de pago
4. ⏳ Probar con diferentes métodos de entrega
5. ⏳ Verificar auto-refresh en todas las páginas
