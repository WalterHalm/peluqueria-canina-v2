# 📘 DOCUMENTO DE DESARROLLO - Peluquería Canina PRO

**Versión:** 19.0.2.0  
**Última actualización:** 2026-02-13  
**Estado:** ETAPA 1 Completada + Mejoras Implementadas ✅

---

## 📋 ÍNDICE

1. [Arquitectura General](#arquitectura-general)
2. [Modelos Implementados](#modelos-implementados)
3. [Flujo de Trabajo](#flujo-de-trabajo)
4. [Historial de Cambios](#historial-de-cambios)
5. [Errores Solucionados](#errores-solucionados)
6. [Próximas Implementaciones](#próximas-implementaciones)

---

## 🏗️ ARQUITECTURA GENERAL

### Dependencias
```python
'depends': [
    'peluqueria_canina',  # Módulo base
    'account',            # Facturación
    'stock',              # Productos
    'calendar',           # Agenda
]
```

### Estructura de Archivos
```
peluqueria_canina_pro/
├── models/
│   ├── __init__.py
│   ├── servicio.py          # Catálogo de servicios
│   ├── turno.py             # Sistema de turnos mejorado
│   ├── visita.py            # Historial y centro de costos
│   ├── mascota.py           # Extensión del modelo base
│   └── dashboard.py         # Dashboard dinámico con KPIs
├── views/
│   ├── dashboard_views.xml  # KPIs y resumen
│   ├── servicio_views.xml   # Vistas de servicios
│   ├── turno_views.xml      # Vistas de turnos
│   ├── visita_views.xml     # Vistas de visitas
│   └── menu_views.xml       # Menú principal
├── security/
│   └── ir.model.access.csv  # Permisos
├── data/
│   └── servicio_data.xml    # Datos iniciales
├── static/
│   └── src/css/
│       └── dashboard.css    # Estilos responsive
└── reports/
    └── reporte_financiero.xml
```

---

## 📦 MODELOS IMPLEMENTADOS

### 1. MODELO: peluqueria.servicio

**Propósito:** Catálogo de servicios ofrecidos por la peluquería con control de precios y costos.

**Archivo:** `models/servicio.py`

#### Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | Char | Nombre del servicio (ej: "Baño Completo") |
| `descripcion` | Text | Descripción detallada |
| `precio` | Monetary | Precio de venta al cliente |
| `costo_estimado` | Monetary | Costo estimado (calculado desde productos) |
| `duracion` | Float | Duración en horas |
| `activo` | Boolean | Si está disponible |
| `categoria` | Selection | Baño/Corte/Deslanado/Especial |
| `producto_ids` | One2many | Productos con cantidad específica |

#### Campos Calculados
- `margen`: ((precio - costo_estimado) / precio) * 100
- `costo_estimado`: sum(producto_ids.costo_total) - Calculado automáticamente

#### Vistas Implementadas
- ✅ **Kanban**: Cards con precio, duración y margen
- ✅ **List**: Tabla con filtros por categoría
- ✅ **Form**: Formulario completo con productos
- ✅ **Search**: Búsqueda por nombre y categoría

#### Datos Iniciales
```xml
- Baño Completo ($2,000)
- Corte de Pelo ($1,500)
- Deslanado ($2,500)
- Corte de Uñas ($500)
- Limpieza de Oídos ($400)
- Baño Medicado ($2,800)
```

#### Mejoras Realizadas
- ✅ Agregado campo `categoria` para clasificación
- ✅ Cálculo automático de ganancia y margen
- ✅ Relación One2many con productos (cantidad específica)
- ✅ Vista kanban responsive con colores
- ✅ Margen corregido: ahora muestra porcentaje real (25% en lugar de 0.25)
- ✅ Costo estimado calculado automáticamente desde productos
- ✅ Unidad de medida editable con conversión automática
- ✅ Domain dinámico: solo UoM de la misma categoría (kg/g, L/ml)

#### Errores Solucionados
- ✅ **Margen mostraba 8500%**: Faltaba multiplicar por 100 en el cálculo
- ✅ **Vista kanban no era predeterminada**: Agregado view_id en acción
- ✅ **Productos no se listaban**: Cambiado domain de 'type' a campo correcto

---

### 1.1 MODELO: peluqueria.servicio.producto

**Propósito:** Líneas de productos con cantidad específica por servicio.

**Archivo:** `models/servicio.py` (clase interna)

#### Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `servicio_id` | Many2one | Servicio relacionado |
| `producto_id` | Many2one | Producto usado |
| `cantidad` | Float | Cantidad que se usa del producto |
| `uom_id` | Many2one | Unidad de medida (editable) |
| `uom_category_id` | Many2one | Categoría UoM (para domain) |
| `costo_unitario` | Float | Costo del producto |
| `costo_total` | Float | Calculado con conversión UoM |

#### Características
- ✅ Conversión automática entre unidades de medida
- ✅ Domain dinámico: solo UoM de la misma categoría
- ✅ Ejemplo: Shampoo 350g → usar 20g (conversión automática)
- ✅ Cálculo de costo considerando la conversión

---

### 2. MODELO: peluqueria.turno

**Propósito:** Sistema de agenda mejorado con estados y control de flujo.

**Archivo:** `models/turno.py`

#### Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | Char | Número de turno (secuencia) |
| `mascota_id` | Many2one | Mascota a atender |
| `cliente_id` | Many2one | Cliente (related de mascota) |
| `fecha_hora` | Datetime | Fecha y hora del turno |
| `servicio_ids` | Many2many | Servicios solicitados |
| `duracion_estimada` | Float | Calculada de servicios |
| `empleado_id` | Many2one | Peluquero asignado |
| `estado` | Selection | Estado del turno |
| `visita_id` | Many2one | Visita generada |

#### Estados del Turno
```python
[
    ('borrador', 'Borrador'),
    ('confirmado', 'Confirmado'),
    ('en_proceso', 'En Proceso'),
    ('completado', 'Completado'),
    ('cancelado', 'Cancelado'),
    ('no_asistio', 'No Asistió')
]
```

#### Flujo de Estados
```
Borrador → Confirmado → En Proceso → Completado
                ↓            ↓
           Cancelado    No Asistió
```

#### Métodos Principales
- `action_confirmar()`: Cambia estado a confirmado
- `action_iniciar()`: Cambia a en_proceso
- `action_completar()`: Crea visita automáticamente con productos desde servicios
- `action_cancelar()`: Cancela el turno
- `action_no_asistio()`: Marca como no asistió

#### Vistas Implementadas
- ✅ **Calendar**: Vista de calendario con colores por estado
- ✅ **Kanban**: Agrupado por estado
- ✅ **List**: Tabla con filtros
- ✅ **Form**: Formulario con botones de acción

#### Mejoras Realizadas
- ✅ Sistema de estados completo
- ✅ Generación automática de visita al completar
- ✅ Copia automática de productos desde servicios a visita
- ✅ Cálculo de duración desde servicios
- ✅ Colores visuales por estado
- ✅ Validaciones de flujo
- ✅ Vista calendario como predeterminada
- ✅ Chatter estándar de Odoo 19

#### Errores Solucionados
- Ninguno registrado

---

### 3. MODELO: peluqueria.visita

**Propósito:** Historial de atenciones con centro de costos integrado.

**Archivo:** `models/visita.py`

#### Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | Char | Número de visita (secuencia) |
| `mascota_id` | Many2one | Mascota atendida |
| `cliente_id` | Many2one | Cliente (related) |
| `fecha` | Datetime | Fecha de atención |
| `turno_id` | Many2one | Turno origen |
| `servicio_ids` | Many2many | Servicios realizados |
| `producto_line_ids` | One2many | Productos utilizados |
| `empleado_id` | Many2one | Peluquero |
| `state` | Selection | Estado de la visita |
| `factura_id` | Many2one | Factura generada |

#### Centro de Costos (Campos Calculados)
| Campo | Tipo | Cálculo |
|-------|------|---------|
| `precio_servicios` | Monetary | Suma de precios de servicios |
| `costo_productos` | Monetary | Suma de costos de productos |
| `otros_gastos` | Monetary | Gastos adicionales (manual) |
| `costo_total` | Monetary | costo_productos + otros_gastos |
| `total_venta` | Monetary | precio_servicios |
| `ganancia` | Monetary | total_venta - costo_total |
| `margen_porcentaje` | Float | (ganancia / total_venta) * 100 |

#### Estados de Visita
```python
[
    ('borrador', 'Borrador'),
    ('confirmado', 'Confirmado'),
    ('facturado', 'Facturado'),
    ('cancelado', 'Cancelado')
]
```

#### Métodos Principales
- `action_confirmar()`: Confirma la visita
- `action_generar_factura()`: Crea factura en account.move
- `action_ver_factura()`: Abre la factura
- `action_cancelar()`: Cancela (valida factura)

#### Vistas Implementadas
- ✅ **Kanban**: Cards con foto, ganancia destacada
- ✅ **List**: Tabla con totales
- ✅ **Form**: Formulario con centro de costos destacado
- ✅ **Search**: Filtros por estado, fecha, cliente

#### Características Especiales
- 🎨 **Centro de Costos Visual**: Sección destacada con colores
- 📊 **Cálculo Automático**: Todos los totales se calculan en tiempo real
- 🔗 **Integración Contable**: Genera facturas en Odoo
- 📸 **Fotos Antes/Después**: Campos de imagen
- 📝 **Notas**: Observaciones y notas internas

#### Mejoras Realizadas
- ✅ Centro de costos completo
- ✅ Integración con facturación
- ✅ Validaciones de cliente y servicios
- ✅ Cálculo automático de ganancias
- ✅ Vista responsive del centro de costos
- ✅ Productos precargados desde servicios al crear desde turno
- ✅ Posibilidad de agregar más productos manualmente
- ✅ Imágenes antes/después con attachment=True (guardado en BD)
- ✅ Chatter estándar de Odoo 19

#### Errores Solucionados
- ❌ **Error**: Comparación con string traducido en create()
  - **Solución**: Cambiar `vals.get('name', _('Nuevo')) == _('Nuevo')` por `not vals.get('name') or vals.get('name') == 'Nuevo'`
  - **Fecha**: 2024
  - **Commit**: Inicial

- ❌ **Error**: Falta validación de cliente y servicios en facturación
  - **Solución**: Agregar ValidationError antes de crear factura
  - **Fecha**: 2024
  - **Commit**: Inicial

- ❌ **Error**: Clase VisitaServicio duplicada e innecesaria
  - **Solución**: Eliminar clase, usar Many2many directo
  - **Fecha**: 2024
  - **Commit**: Inicial

---

### 4. MODELO: peluqueria.visita.producto

**Propósito:** Líneas de productos utilizados en cada visita.

**Archivo:** `models/visita.py` (clase interna)

#### Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `visita_id` | Many2one | Visita relacionada |
| `producto_id` | Many2one | Producto usado |
| `cantidad` | Float | Cantidad utilizada |
| `uom_id` | Many2one | Unidad de medida (editable) |
| `uom_category_id` | Many2one | Categoría UoM (para domain) |
| `costo_unitario` | Float | Costo del producto (editable) |
| `subtotal_costo` | Float | Calculado con conversión UoM |

#### Características
- ✅ Cálculo automático de subtotal con conversión UoM
- ✅ Relación con product.product de Odoo
- ✅ Filtro solo productos tipo 'product'
- ✅ Unidad de medida editable con domain de misma categoría
- ✅ Costo unitario editable para ajustes manuales

---

### 5. MODELO: peluqueria.mascota (Extensión)

**Propósito:** Extender modelo base con relaciones a nuevos modelos.

**Archivo:** `models/mascota.py`

#### Campos Agregados
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `turno_ids` | One2many | Turnos de la mascota (herencia en PRO) |
| `visita_ids` | One2many | Visitas de la mascota (herencia en PRO) |
| `turno_count` | Integer | Cantidad de turnos |
| `visita_count` | Integer | Cantidad de visitas |
| `ultima_visita` | Date | Fecha última visita |
| `proximo_turno` | Datetime | Próximo turno confirmado |

#### Métodos Agregados
- `action_ver_turnos()`: Abre lista de turnos
- `action_ver_visitas()`: Abre historial de visitas filtrado
- `action_nuevo_turno()`: Crea turno rápido

#### Mejoras Realizadas
- ✅ Smart buttons en vista de mascota
- ✅ Contadores de turnos y visitas
- ✅ Acceso rápido al historial
- ✅ Campo turno_ids agregado en módulo PRO (herencia)

---

### 6. MODELO: peluqueria.dashboard

**Propósito:** Dashboard dinámico con KPIs en tiempo real y filtros.

**Archivo:** `models/dashboard.py`

#### Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fecha_desde` | Date | Filtro fecha inicio |
| `fecha_hasta` | Date | Filtro fecha fin |
| `servicio_id` | Many2one | Filtro por servicio |
| `periodo` | Selection | Diario/Mensual/Trimestral |
| `turnos_hoy` | Integer | KPI turnos del día |
| `ventas_hoy` | Monetary | KPI ventas del día |
| `turnos_pendientes` | Integer | KPI turnos pendientes |
| `ganancia_hoy` | Monetary | KPI ganancia del día |
| `ventas_periodo` | Monetary | Ventas del periodo |
| `costos_periodo` | Monetary | Costos del periodo |
| `ganancia_periodo` | Monetary | Ganancia del periodo |
| `margen_periodo` | Float | Margen % del periodo |

#### Métodos Principales
- `action_ver_turnos_hoy()`: Abre turnos filtrados por hoy
- `action_ver_ventas_hoy()`: Abre visitas del día
- `action_ver_turnos_pendientes()`: Abre turnos pendientes

#### Características
- ✅ KPIs dinámicos calculados en tiempo real
- ✅ Filtros por fecha, servicio y periodo
- ✅ Resumen ajustable: diario, mensual o trimestral
- ✅ KPIs clickeables que redirigen con filtros aplicados
- ✅ Datos reales desde turnos y visitas

---

## 🔄 FLUJO DE TRABAJO

### Flujo Principal: Turno → Visita → Factura

```
1. CREAR TURNO
   ├─ Seleccionar mascota
   ├─ Elegir servicios
   ├─ Asignar fecha/hora
   └─ Estado: Borrador

2. CONFIRMAR TURNO
   └─ Estado: Confirmado

3. INICIAR ATENCIÓN
   └─ Estado: En Proceso

4. COMPLETAR TURNO
   ├─ Estado: Completado
   └─ Genera automáticamente VISITA

5. VISITA CREADA
   ├─ Copia servicios del turno
   ├─ Agregar productos usados
   ├─ Ver ganancia calculada
   └─ Estado: Borrador

6. CONFIRMAR VISITA
   └─ Estado: Confirmado

7. GENERAR FACTURA
   ├─ Crea account.move
   ├─ Líneas desde servicios
   └─ Estado: Facturado
```

### Flujo Alternativo: Visita Directa

```
1. CREAR VISITA MANUAL
   ├─ Sin turno previo
   ├─ Seleccionar mascota
   └─ Agregar servicios

2. AGREGAR PRODUCTOS
   └─ Productos utilizados

3. VER CENTRO DE COSTOS
   ├─ Precio servicios
   ├─ Costo productos
   └─ Ganancia calculada

4. GENERAR FACTURA
   └─ Facturación directa
```

---

## 📊 VISTAS Y UI

### Dashboard (dashboard_views.xml)

**Características:**
- 📊 KPIs del día dinámicos (turnos, ventas, ganancias)
- 🔍 Filtros por fecha, servicio y periodo
- 📅 Resumen ajustable: diario, mensual, trimestral
- 👆 KPIs clickeables que redirigen con filtros
- 📱 Responsive (mobile, tablet, desktop)

**CSS:** `static/src/css/dashboard.css`
- Media queries para diferentes pantallas
- Colores corporativos
- Animaciones suaves

### Vistas Kanban

**Características comunes:**
- 🎨 Colores por estado
- 📸 Imágenes destacadas
- 💰 Información financiera visible
- 📱 Responsive design
- ⚡ Acciones rápidas

### Vistas Calendar

**Turno Calendar:**
- 📅 Vista mensual/semanal/diaria
- 🎨 Colores por estado
- ⏰ Duración visual
- 👤 Filtro por empleado

---

## 🔐 SEGURIDAD

### Grupos de Acceso
```csv
peluqueria_canina_pro.group_user    # Usuario básico
peluqueria_canina_pro.group_manager # Administrador
```

### Permisos por Modelo
| Modelo | Usuario | Manager |
|--------|---------|---------|
| servicio | Read | All |
| servicio.producto | All | All |
| turno | All | All |
| visita | All | All |
| visita.producto | All | All |
| dashboard | All | All |

---

## 📈 HISTORIAL DE CAMBIOS

### Versión 19.0.2.1 (FILTROS Y AGRUPAMIENTOS)

**Fecha:** 2026-02-13

**Implementaciones:**
- ✅ Filtros avanzados en Turnos (hoy, atrasados, confirmados, semana, mes)
- ✅ Agrupamientos en Turnos (cliente, mascota, empleado, estado, fecha)
- ✅ Filtros avanzados en Visitas (hoy, semana, mes, terminadas, facturadas, con/sin ganancia)
- ✅ Agrupamientos en Visitas (cliente, mascota, empleado, estado, fecha, mes)
- ✅ Búsqueda por múltiples campos (mascota, cliente, servicio, empleado)

**Archivos Modificados:**
- `views/turno_views.xml` (vista search agregada)
- `views/visita_views.xml` (vista search agregada)
- `DESARROLLO.md` (documentación actualizada)

---

### Versión 19.0.2.0 (MEJORAS POST-ETAPA 1)

**Fecha:** 2026-02-13

**Implementaciones:**
- ✅ Dashboard dinámico con datos reales
- ✅ Filtros en dashboard (fecha, servicio, periodo)
- ✅ KPIs clickeables con redirección
- ✅ Productos con cantidad específica en servicios
- ✅ Unidad de medida editable con conversión automática
- ✅ Productos precargados en visitas desde servicios
- ✅ Imágenes antes/después con guardado en BD
- ✅ Lista de turnos en vista de mascota (módulo base)
- ✅ Chatter estándar Odoo 19 en todas las vistas
- ✅ Corrección margen porcentual (8500% → 85%)

**Archivos Modificados:**
- `models/dashboard.py` (NUEVO)
- `models/servicio.py` (productos con UoM)
- `models/turno.py` (copia productos a visita)
- `models/visita.py` (UoM editable, imágenes)
- `views/dashboard_views.xml` (filtros UI)
- `views/servicio_views.xml` (UoM con domain)
- `views/visita_views.xml` (UoM, imágenes)
- `views/turno_views.xml` (chatter)
- `security/ir.model.access.csv` (nuevos permisos)
- `peluqueria_canina/models/models.py` (turno_ids)
- `peluqueria_canina/views/mascotas.xml` (lista turnos)

---

### Versión 19.0.1.0 (ETAPA 1)

**Fecha:** 2024

**Implementaciones:**
- ✅ Modelo Servicio completo
- ✅ Modelo Turno con estados
- ✅ Modelo Visita con centro de costos
- ✅ Dashboard con KPIs
- ✅ Integración con facturación
- ✅ Vistas responsive
- ✅ Datos iniciales de servicios

**Archivos Creados:**
- `models/servicio.py`
- `models/turno.py`
- `models/visita.py`
- `models/mascota.py`
- `views/dashboard_views.xml`
- `views/servicio_views.xml`
- `views/turno_views.xml`
- `views/visita_views.xml`
- `views/menu_views.xml`
- `security/ir.model.access.csv`
- `data/servicio_data.xml`
- `static/src/css/dashboard.css`

---

## 🐛 ERRORES SOLUCIONADOS

### Error #1: Comparación con String Traducido
**Modelo:** peluqueria.visita  
**Método:** create()  
**Fecha:** 2024  
**Severidad:** Medium

**Descripción:**
```python
# ANTES (Incorrecto)
if vals.get('name', _('Nuevo')) == _('Nuevo'):
```

**Problema:** La comparación con strings traducidos puede fallar en diferentes locales.

**Solución:**
```python
# DESPUÉS (Correcto)
if not vals.get('name') or vals.get('name') == 'Nuevo':
```

---

### Error #2: Falta Validación en Facturación
**Modelo:** peluqueria.visita  
**Método:** action_generar_factura()  
**Fecha:** 2024  
**Severidad:** Medium

**Descripción:** No se validaba la existencia de cliente y servicios antes de crear factura.

**Solución:**
```python
if not self.cliente_id:
    raise ValidationError('Debe seleccionar un cliente antes de generar la factura.')
if not self.servicio_ids:
    raise ValidationError('Debe agregar al menos un servicio antes de generar la factura.')
```

---

### Error #3: Clase Duplicada Innecesaria
**Modelo:** peluqueria.visita.servicio  
**Fecha:** 2024  
**Severidad:** Medium

**Descripción:** Existía clase VisitaServicio que no se usaba (Many2many directo es suficiente).

**Solución:** Eliminar clase completa, mantener solo Many2many en Visita.

---

### Error #4: Inconsistencia de Tipo en Campo Related
**Modelo:** peluqueria.visita.producto  
**Campo:** costo_unitario  
**Fecha:** 2024  
**Severidad:** High

**Descripción:**
```python
# ANTES (Incorrecto)
costo_unitario = fields.Monetary(string='Costo Unitario', 
                                 related='producto_id.standard_price', 
                                 currency_field='currency_id')
```

**Error:** `TypeError: Type of related field peluqueria.visita.producto.costo_unitario is inconsistent with product.product.standard_price`

**Problema:** El campo `standard_price` en `product.product` es de tipo Float, no Monetary.

**Solución:**
```python
# DESPUÉS (Correcto)
costo_unitario = fields.Float(string='Costo Unitario', 
                              related='producto_id.standard_price')
subtotal_costo = fields.Float(string='Subtotal', 
                              compute='_compute_subtotal', 
                              store=True)
```

---

### Error #5: Referencia a Modelo Eliminado en Security
**Archivo:** security/ir.model.access.csv  
**Fecha:** 2024  
**Severidad:** High

**Error:** `No matching record found for external id 'model_peluqueria_visita_servicio' in field 'Model'`

**Problema:** Se eliminó la clase `VisitaServicio` pero quedó la referencia en el CSV de seguridad.

**Solución:**
```csv
# ELIMINAR esta línea:
access_peluqueria_visita_servicio,access_peluqueria_visita_servicio,model_peluqueria_visita_servicio,,1,1,1,1
```

---

### Error #6: Valor Inválido en Target de Action
**Archivo:** views/dashboard_views.xml  
**Campo:** target  
**Fecha:** 2024  
**Severidad:** High

**Error:** `ValueError: Wrong value for ir.actions.act_window.target: 'inline'`

**Problema:** El valor 'inline' no es válido para el campo target en Odoo 19.

**Solución:**
```xml
<!-- ANTES (Incorrecto) -->
<field name="target">inline</field>

<!-- DESPUÉS (Correcto) -->
<field name="target">main</field>
```

**Valores válidos:** 'current', 'new', 'main', 'fullscreen'

---

### Error #7: Group By en Campo Monetary
**Archivo:** views/servicio_views.xml  
**Vista:** search  
**Fecha:** 2024  
**Severidad:** High

**Error:** `ParseError: La definición de la vista peluqueria.servicio.search no es válida`

**Problema:** No se puede agrupar por campos Monetary en Odoo.

**Solución:**
```xml
<!-- ELIMINAR esta línea: -->
<filter string="Precio" name="group_precio" context="{'group_by': 'precio'}"/>
```

---

### Error #8: Referencia a Modelo Eliminado en Compute
**Modelo:** peluqueria.servicio  
**Método:** _compute_visita_count()  
**Fecha:** 2024  
**Severidad:** High

**Problema:** Referencia al modelo eliminado `peluqueria.visita.servicio`.

**Solución:**
```python
# ANTES (Incorrecto)
record.visita_count = self.env['peluqueria.visita.servicio'].search_count([
    ('servicio_id', '=', record.id)
])

# DESPUÉS (Correcto)
record.visita_count = self.env['peluqueria.visita'].search_count([
    ('servicio_ids', 'in', record.id)
])
```

---

### Error #9: Dashboard Intenta Guardar Registro
**Archivo:** views/dashboard_views.xml  
**Fecha:** 2024  
**Severidad:** High

**Error:** `Missing required value for the field 'Mascota' (mascota_id)`

**Problema:** El dashboard usa un formulario de `peluqueria.turno` pero no debe permitir guardar.

**Solución:**
```xml
<field name="context">{'form_view_initial_mode': 'readonly', 'create': False, 'edit': False, 'delete': False}</field>
```

---

### Error #10: Margen Mostraba 8500%
**Modelo:** peluqueria.servicio  
**Método:** _compute_margen()  
**Fecha:** 2026-02-13  
**Severidad:** High

**Descripción:** El margen se calculaba como decimal (0.85) pero se mostraba con widget percentage que multiplica por 100.

**Solución:**
```python
# ANTES (Incorrecto)
record.margen = ((record.precio - record.costo_estimado) / record.precio)

# DESPUÉS (Correcto)
record.margen = ((record.precio - record.costo_estimado) / record.precio) * 100
```

Y remover `widget="percentage"` de las vistas.

---

### Error #11: Dashboard Usaba Modelo Incorrecto
**Archivo:** views/dashboard_views.xml  
**Fecha:** 2026-02-13  
**Severidad:** High

**Problema:** Dashboard usaba `peluqueria.turno` como modelo, causando error al intentar guardar.

**Solución:** Crear modelo dedicado `peluqueria.dashboard` con campos computados.

---

### Error #12: Productos No Se Copiaban a Visita
**Modelo:** peluqueria.turno  
**Método:** action_completar()  
**Fecha:** 2026-02-13  
**Severidad:** Medium

**Problema:** Al completar turno, los productos definidos en servicios no se copiaban a la visita.

**Solución:**
```python
producto_lines = []
for servicio in self.servicio_ids:
    for prod_line in servicio.producto_ids:
        producto_lines.append((0, 0, {
            'producto_id': prod_line.producto_id.id,
            'cantidad': prod_line.cantidad,
        }))
```

---

### Error #13: Imágenes No Se Podían Subir
**Modelo:** peluqueria.visita  
**Campos:** imagen_antes, imagen_despues  
**Fecha:** 2026-02-13  
**Severidad:** Medium

**Problema:** Faltaba `attachment=True` y widget incorrecto en vista.

**Solución:**
```python
imagen_antes = fields.Image(string='Foto Antes', max_width=1024, max_height=1024, attachment=True)
```

```xml
<field name="imagen_antes" widget="image" class="oe_avatar"/>
```

---

### Error #14: Chatter Mostraba Formato Incorrecto
**Archivos:** turno_views.xml, visita_views.xml  
**Fecha:** 2026-02-13  
**Severidad:** Medium

**Problema:** Uso manual de `message_follower_ids` y `message_ids` en lugar del widget estándar.

**Solución:**
```xml
<!-- ANTES (Incorrecto) -->
<div class="oe_chatter">
    <field name="message_follower_ids" groups="base.group_user"/>
    <field name="message_ids"/>
</div>

<!-- DESPUÉS (Correcto) -->
<chatter/>
```

---

### Error #15: SyntaxError en Modelo Historial
**Archivo:** models/historial.py  
**Fecha:** 2026-02-13  
**Severidad:** Critical

**Error:** `SyntaxError: unexpected character after line continuation character`

**Problema:** Archivo `historial.py` contenía `\n` literal en lugar de salto de línea real en línea 21.

**Solución:** Eliminar import del modelo historial ya que no es necesario para el flujo de trabajo.

```python
# ANTES (models/__init__.py)
from . import historial

# DESPUÉS (models/__init__.py)
# Línea eliminada - modelo historial no necesario
```

**Nota:** El modelo `peluqueria.historial` fue creado pero no es necesario. Las visitas terminadas se filtran directamente desde `peluqueria.visita` con domain `[('state', '=', 'terminado')]`.

---

## 🚀 PRÓXIMAS IMPLEMENTACIONES

### ETAPA 2: Reportes Financieros
- [ ] Reporte de ventas por período
- [ ] Reporte de servicios más solicitados
- [ ] Reporte de ganancias por empleado
- [ ] Gráficos de tendencias
- [ ] Exportación a Excel/PDF

### ETAPA 3: Recordatorios Automáticos
- [ ] Recordatorio de turno (24hs antes)
- [ ] Recordatorio de visita periódica
- [ ] Email automático
- [ ] SMS/WhatsApp (opcional)

### ETAPA 4: Galería de Fotos
- [ ] Múltiples fotos por visita
- [ ] Galería en kanban
- [ ] Compartir con cliente
- [ ] Antes/después mejorado

### ETAPA 5: Integración WhatsApp
- [ ] Confirmación de turno
- [ ] Envío de fotos
- [ ] Notificación mascota lista
- [ ] Chat integrado

---

## 👨‍💻 GUÍA PARA NUEVOS DESARROLLADORES

### Configuración Inicial
1. Clonar repositorio
2. Instalar `peluqueria_canina` (módulo base)
3. Instalar `peluqueria_canina_pro`
4. Cargar datos de demostración

### Estructura de Código
- **Modelos**: Usar herencia de Odoo 19
- **Vistas**: Responsive con CSS moderno
- **Seguridad**: Siempre definir permisos
- **Datos**: Usar XML para datos iniciales

### Convenciones
- Nombres en español para campos visibles
- Nombres técnicos en inglés para código
- Comentarios en español
- Docstrings en español

### Testing
- Probar en móvil, tablet y desktop
- Validar cálculos de centro de costos
- Verificar flujo completo turno→visita→factura
- Probar permisos por grupo

---

## 📞 CONTACTO Y SOPORTE

**Documentación Odoo 19:** https://www.odoo.com/documentation/19.0/  
**Repositorio:** [Pendiente]  
**Issues:** [Pendiente]

---

**Última actualización:** 2026-02-13  
**Mantenido por:** Equipo de Desarrollo Peluquería Canina PRO
