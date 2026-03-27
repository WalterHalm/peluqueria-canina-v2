# Documento de Configuraciones Nativas — Real Estate Odoo 19

> Este documento detalla TODAS las configuraciones que se pueden resolver con módulos nativos de Odoo 19 Enterprise, sin desarrollo custom.

---

## ÍNDICE

1. [Módulos a Instalar](#1-módulos-a-instalar)
2. [Configuración del Módulo de Rental (Alquileres)](#2-configuración-del-módulo-de-rental)
3. [Configuración de Productos — Propiedades de Alquiler](#3-productos-propiedades-de-alquiler)
4. [Configuración de Productos — Propiedades de Venta](#4-productos-propiedades-de-venta)
5. [Configuración del eCommerce (Website Sale + Renting)](#5-configuración-del-ecommerce)
6. [Configuración de Pagos Online](#6-configuración-de-pagos-online)
7. [Configuración de WhatsApp](#7-configuración-de-whatsapp)
8. [Configuración del Sitio Web](#8-configuración-del-sitio-web)
9. [Configuración de Usuarios Portal (Propietarios)](#9-usuarios-portal-propietarios)
10. [Configuración de CRM para Captación](#10-crm-para-captación)

---

## 1. Módulos a Instalar

### Módulos Enterprise (obligatorios)
| Módulo | Nombre Técnico | Propósito |
|--------|---------------|-----------|
| Rental | `sale_renting` | Motor de alquileres: productos rentables, pricing por duración, gestión pickup/return |
| eCommerce Rental | `website_sale_renting` | Venta de alquileres online con date picker, pricing table en frontend |
| Rental Stock | `sale_stock_renting` | Control de disponibilidad de stock para alquileres |
| eCommerce Rental Stock | `website_sale_stock_renting` | Disponibilidad en tiempo real en el frontend |
| WhatsApp | `whatsapp` | Integración WhatsApp Business API |
| WhatsApp eCommerce | `whatsapp_website_sale` | WhatsApp integrado con eCommerce |

### Módulos Community (obligatorios)
| Módulo | Nombre Técnico | Propósito |
|--------|---------------|-----------|
| Website | `website` | Constructor de sitio web |
| eCommerce | `website_sale` | Tienda online, catálogo de productos |
| Payment Engine | `payment` | Motor de pagos |
| Contacts | `contacts` | Gestión de contactos |
| CRM | `crm` | Gestión de leads para captación |
| Website Payment | `website_payment` | Pagos en el sitio web |

### Módulos Opcionales (recomendados)
| Módulo | Nombre Técnico | Propósito |
|--------|---------------|-----------|
| Website Comparison | `website_sale_comparison` | Comparar propiedades |
| Website Wishlist | `website_sale_wishlist` | Lista de favoritos |
| Sale Management Renting | `sale_management_renting` | Plantillas de cotización para alquileres |
| Rental CRM | `sale_renting_crm` | Vincular leads con alquileres |

### Paso a paso para instalar:
1. Activar **Modo Desarrollador**: Ajustes → General → Modo Desarrollador (activar)
2. Ir a **Aplicaciones** → Actualizar lista de aplicaciones
3. Buscar e instalar en este orden:
   - `website` (si no está instalado)
   - `sale_renting` → Esto instala automáticamente `sale` y `web_gantt`
   - `website_sale` → eCommerce
   - `website_sale_renting` → Se auto-instala al tener `website_sale` + `sale_renting`
   - `sale_stock_renting` → Se auto-instala al tener `sale_renting` + `sale_stock`
   - `whatsapp` → WhatsApp Business
   - `crm` → CRM para captación

---

## 2. Configuración del Módulo de Rental

### 2.1 Ajustes Generales del Rental
**Ruta:** Alquiler → Configuración → Ajustes

1. **Períodos de Recurrencia**: Configurar las duraciones disponibles
   - Ir a Alquiler → Configuración → Períodos de Recurrencia
   - Crear los períodos necesarios:
     - `1 Noche` (unit: day, duration: 1, overnight: ✓)
     - `1 Semana` (unit: week, duration: 1)
     - `1 Mes` (unit: month, duration: 1)
   - **IMPORTANTE para alquiler por días**: Usar el tipo "overnight" (noche) que es el más adecuado para alquileres tipo Airbnb/Booking donde se cobra por noche

2. **Días no disponibles**: Configurar días de la semana donde no se permite pickup/return
   - Ajustes → Rental → Unavailability Days
   - Marcar los días que no se permiten (ej: ninguno para máxima flexibilidad)

3. **Duración mínima de alquiler**:
   - Ajustes → Rental → Minimum Rental Duration
   - Configurar: 1 noche mínimo (o según política del negocio)

4. **Multas por retraso**:
   - Se configuran a nivel de producto (extra_hourly, extra_daily)
   - Configurar el producto de "Rental Delay Cost" en Ajustes → Rental → Extra Product

### 2.2 Flujo Operativo del Rental (cómo funciona nativamente)
El módulo `sale_renting` maneja este flujo:

```
Cotización → Confirmación → Pickup (entrega) → Return (devolución) → Facturación
     ↓            ↓              ↓                    ↓
   draft        sale          delivered            returned
```

- **Pickup**: El huésped recibe las llaves/acceso → se marca qty_delivered
- **Return**: El huésped devuelve → se marca qty_returned
- **Late fees**: Si devuelve tarde, se genera línea automática de multa

### 2.3 Vista Gantt (Schedule)
- Acceder desde Alquiler → Schedule
- Vista Gantt que muestra todas las reservas en timeline
- Permite crear nuevas reservas arrastrando
- Colores por estado: púrpura (borrador), azul (reservado), naranja (en uso), verde (devuelto), rojo (atrasado)

---

## 3. Productos — Propiedades de Alquiler

### 3.1 Crear Categoría de Productos
**Ruta:** Inventario → Configuración → Categorías de Producto

1. Crear categoría: **"Propiedades en Alquiler"**
   - Categoría padre: (ninguna)
   - Método de costeo: Estándar

2. Crear subcategorías si es necesario:
   - Apartamentos
   - Casas
   - Habitaciones
   - Villas

### 3.2 Crear Atributos de Producto
**Ruta:** eCommerce → Configuración → Atributos

Crear los siguientes atributos para filtrar propiedades:

| Atributo | Tipo de Visualización | Valores |
|----------|----------------------|---------|
| Ubicación/Zona | Radio | Centro, Playa, Montaña, Suburbio, etc. |
| Habitaciones | Radio | 1, 2, 3, 4, 5+ |
| Capacidad (huéspedes) | Radio | 2, 4, 6, 8, 10+ |
| Amenidades | Checkbox (multi) | WiFi, Piscina, Estacionamiento, A/C, Cocina, Lavadora |
| Tipo de Propiedad | Radio | Apartamento, Casa, Villa, Habitación |

### 3.3 Crear un Producto de Alquiler (Propiedad)
**Ruta:** Alquiler → Productos → Crear

Para cada propiedad:

1. **Pestaña General:**
   - Nombre: "Apartamento Vista al Mar - Zona Playa" (nombre descriptivo)
   - Tipo de producto: **Almacenable** (para control de disponibilidad)
   - Marcar: **☑ Rental** (rent_ok = True)
   - Desmarcar: ☐ Sales (sale_ok = False) — solo alquiler
   - Precio de venta: Dejar en 0 (se usa pricing rules)
   - Categoría: Propiedades en Alquiler

2. **Pestaña Atributos y Variantes:**
   - Agregar los atributos creados (Ubicación, Habitaciones, etc.)
   - Esto genera variantes si es necesario, o usar como filtros

3. **Pestaña Pricing (Custom Pricings):**
   - Agregar reglas de precio:
     - Período: 1 Noche → Precio: $XX USD
     - Período: 1 Semana → Precio: $XX USD (con descuento)
     - Período: 1 Mes → Precio: $XX USD (con mayor descuento)
   - Se pueden crear pricings por lista de precios (temporada alta/baja)

4. **Pestaña Descripción eCommerce:**
   - Descripción completa de la propiedad
   - Agregar imágenes (múltiples fotos)
   - Esta descripción se muestra en el sitio web

5. **Pestaña Inventario:**
   - Cantidad disponible: **1** (una propiedad = 1 unidad)
   - Esto controla que no se pueda reservar si ya está ocupada

6. **Pestaña Multas:**
   - Hourly Fine: Multa por hora de retraso
   - Daily Fine: Multa por día de retraso

### 3.4 Listas de Precios por Temporada
**Ruta:** eCommerce → Configuración → Listas de Precios

1. Crear lista: **"Temporada Alta"**
   - Moneda: USD/COP según corresponda
   - En la pestaña "Time-based rules" agregar pricing rules con precios más altos

2. Crear lista: **"Temporada Baja"**
   - Precios reducidos

3. Asignar listas de precios por fecha o por grupo de clientes

---

## 4. Productos — Propiedades de Venta

### 4.1 Análisis: ¿Se puede usar nativamente?

**SÍ**, las propiedades en venta se pueden manejar como productos normales de eCommerce:

- Tipo de producto: **Servicio** (no necesita stock, una propiedad en venta es única)
- Marcar: **☑ Sales** (sale_ok = True)
- Desmarcar: ☐ Rental (rent_ok = False)
- Precio: Precio de venta de la propiedad

**Limitaciones nativas:**
- No hay un flujo inmobiliario de "oferta → contraoferta → cierre"
- El checkout es un flujo de eCommerce estándar (carrito → pago)
- Para propiedades de venta, probablemente sea mejor usar el flujo de **"Contactar"** en lugar de "Agregar al carrito"

### 4.2 Crear Producto de Venta (Propiedad)
**Ruta:** eCommerce → Productos → Crear

1. **General:**
   - Nombre: "Casa 3 Habitaciones - Zona Norte"
   - Tipo: **Servicio**
   - ☑ Sales, ☐ Rental
   - Precio: $150,000 USD
   - Categoría: Crear **"Propiedades en Venta"**

2. **Atributos:** Reutilizar los mismos (Ubicación, Habitaciones, etc.)

3. **Descripción eCommerce:** Fotos, descripción detallada, metros cuadrados, etc.

4. **Publicar en sitio web:** ☑ Publicado

### 4.3 Separar Alquileres y Ventas en el Sitio Web
Para tener secciones separadas (/alquileres y /ventas):

**Opción nativa:** Usar **Categorías de eCommerce** como filtro:
1. Ir a eCommerce → Configuración → Categorías de eCommerce
2. Crear: "Alquileres" y "Ventas"
3. Asignar cada producto a su categoría
4. En el sitio web, crear menús que apunten a:
   - `/shop?category=alquileres`
   - `/shop?category=ventas`

---

## 5. Configuración del eCommerce

### 5.1 Ajustes del eCommerce
**Ruta:** Sitio Web → Configuración → Ajustes

1. **Catálogo de productos:**
   - ☑ Atributos de producto (para filtros)
   - ☑ Comparación de productos (opcional)
   - ☑ Lista de deseos (opcional)

2. **Checkout:**
   - Configurar política de checkout (con o sin cuenta)
   - ☑ Permitir checkout como invitado (para facilitar reservas)

3. **Rental Datepicker en Shop:**
   - Activar la vista `website_sale_renting.shop_rental_datepicker_opt`
   - Esto agrega el selector de fechas en la página de tienda
   - **Ruta:** Sitio Web → Personalizar → activar "Rental Period" en la barra lateral

### 5.2 Snippet de Búsqueda de Rental
El módulo `website_sale_renting` incluye un snippet `s_rental_search` que permite:
- Seleccionar fecha de inicio y fin
- Buscar propiedades disponibles en ese rango
- Se puede arrastrar desde el editor de sitio web a cualquier página

**Cómo usarlo:**
1. Ir al editor del sitio web
2. En la barra de snippets, buscar "Rental Search"
3. Arrastrarlo al banner o homepage
4. Los usuarios podrán buscar por fechas y ver solo propiedades disponibles

### 5.3 Flujo de Reserva Online (Nativo)
```
Usuario visita /shop → Filtra por fechas → Selecciona propiedad →
Ve pricing por duración → Selecciona período → Agrega al carrito →
Checkout → Pago online → Orden confirmada → Pickup automático o manual
```

---

## 6. Configuración de Pagos Online

### 6.1 Proveedores de Pago Disponibles en Odoo 19
Odoo 19 incluye estos proveedores nativos:

| Proveedor | Módulo | Región |
|-----------|--------|--------|
| Stripe | `payment_stripe` | Global |
| PayPal | `payment_paypal` | Global |
| Mercado Pago | `payment_mercado_pago` | LATAM |
| Adyen | `payment_adyen` | Global |
| Authorize.net | `payment_authorize` | USA |
| Redsys | `payment_redsys` | España |
| Flutterwave | `payment_flutterwave` | África |
| Razorpay | `payment_razorpay` | India |

### 6.2 Bold Payment Gateway
**Bold NO tiene módulo nativo en Odoo 19.** Es un proveedor de pagos de Colombia/República Dominicana.

**Opciones:**
1. **Desarrollo custom** (ver documento de desarrollo, Etapa 3)
2. **Alternativa inmediata:** Usar **Stripe** o **Mercado Pago** que sí funcionan en LATAM
3. **Alternativa intermedia:** Usar `payment_custom` para pagos manuales con instrucciones de Bold

### 6.3 Configurar Stripe (alternativa recomendada)
**Ruta:** Facturación → Configuración → Proveedores de Pago

1. Seleccionar **Stripe**
2. Estado: **Habilitado** (o Test para pruebas)
3. Ingresar credenciales:
   - Publishable Key: `<stripe_publishable_key>`
   - Secret Key: `<stripe_secret_key>`
   - Webhook Secret: `<stripe_webhook_secret>`
4. Métodos de pago: Activar tarjetas de crédito/débito
5. Guardar y probar

### 6.4 Configurar Mercado Pago (alternativa LATAM)
1. Seleccionar **Mercado Pago**
2. Ingresar Access Token: `<mercado_pago_access_token>`
3. Activar métodos de pago locales

---

## 7. Configuración de WhatsApp

### 7.1 WhatsApp Business API
**Ruta:** WhatsApp → Configuración → Cuentas WhatsApp

**Prerrequisitos:**
- Cuenta de Meta Business
- Número de WhatsApp Business verificado
- Token de acceso de la API de WhatsApp Business

**Configuración:**
1. Crear cuenta WhatsApp:
   - Nombre: "Inmobiliaria [Nombre]"
   - Phone Number ID: `<whatsapp_phone_id>`
   - Business Account ID: `<whatsapp_business_id>`
   - Access Token: `<whatsapp_access_token>`
   - App Secret: `<whatsapp_app_secret>`

2. Crear plantillas de mensaje:
   - Confirmación de reserva
   - Recordatorio de check-in
   - Recordatorio de check-out
   - Bienvenida a nuevo lead

### 7.2 Botón Flotante de WhatsApp (Sitio Web)
**Esto NO es nativo del módulo `whatsapp`.** El módulo de WhatsApp de Odoo es para enviar mensajes desde el backend, no para un botón flotante en el sitio web.

**Para el botón flotante:** Ver documento de desarrollo (Etapa 1) — es un desarrollo simple con HTML/CSS.

**Alternativa nativa parcial:** Usar el editor del sitio web para agregar un bloque HTML con enlace `https://wa.me/<numero>`.

---

## 8. Configuración del Sitio Web

### 8.1 Páginas que se crean desde el Editor (sin desarrollo)
**Ruta:** Sitio Web → Editor

Estas páginas las vas a crear vos directamente desde el módulo de sitio web:

1. **Homepage (Inicio):**
   - Banner principal con snippet de búsqueda de rental
   - Secciones de propiedades destacadas
   - Call to action

2. **Nosotros (About Us):**
   - Sitio Web → Páginas → Crear nueva página → /nosotros
   - Usar snippets de texto, imágenes, equipo

3. **Contáctenos:**
   - Sitio Web → Páginas → Crear nueva página → /contactenos
   - Usar snippet de formulario de contacto (nativo)
   - El formulario nativo envía a `crm.lead` o `mail.message`

4. **Captación (Deje su propiedad):**
   - Sitio Web → Páginas → Crear nueva página → /captacion
   - Usar snippet de formulario personalizado
   - Configurar que envíe a CRM como lead

5. **Alquileres:**
   - URL: `/shop?category=alquileres` o crear menú personalizado
   - La tienda ya muestra los productos de alquiler con date picker

6. **Ventas:**
   - URL: `/shop?category=ventas`

### 8.2 Menú de Navegación
**Ruta:** Sitio Web → Editor → Menú

Configurar menú:
```
Inicio          → /
Alquileres      → /shop?category=X (ID de categoría alquileres)
Ventas          → /shop?category=Y (ID de categoría ventas)
Nosotros        → /nosotros
Contáctenos     → /contactenos
Captación       → /captacion
```

### 8.3 Redes Sociales
**Ruta:** Sitio Web → Configuración → Ajustes → Social Media

1. Configurar URLs de redes sociales:
   - Facebook: `https://facebook.com/<pagina>`
   - Instagram: `https://instagram.com/<perfil>`
   - Twitter/X: `https://x.com/<perfil>`
2. Los iconos aparecen automáticamente en el footer del sitio web

### 8.4 Idioma Español
**Ruta:** Ajustes → General → Idiomas

1. Activar Español
2. Establecer como idioma por defecto del sitio web
3. Sitio Web → Configuración → Idioma por defecto: Español

---

## 9. Usuarios Portal (Propietarios)

### 9.1 Concepto
Los propietarios de propiedades pueden tener acceso al **Portal de Odoo** para:
- Ver el estado de sus propiedades
- Ver reservas/órdenes de venta
- Ver facturas y pagos
- Comunicarse vía chatter

### 9.2 Configuración de Acceso Portal
**Ruta:** Contactos → Seleccionar contacto → Acción → Otorgar acceso portal

1. Crear contacto del propietario
2. Otorgar acceso portal → Se envía email con credenciales
3. El propietario accede a `/my` y ve:
   - Sus cotizaciones/órdenes
   - Sus facturas
   - Mensajes

### 9.3 Limitaciones Nativas del Portal
**Lo que NO puede hacer un usuario portal nativamente:**
- ❌ Crear/editar productos (propiedades)
- ❌ Subir fotos de propiedades
- ❌ Gestionar precios o disponibilidad
- ❌ Ver calendario de reservas de sus propiedades

**Para que los propietarios puedan cargar sus propiedades:** Se necesita desarrollo custom (ver documento de desarrollo, Etapa 4).

---

## 10. CRM para Captación

### 10.1 Configurar Pipeline de Captación
**Ruta:** CRM → Configuración → Equipos de Ventas

1. Crear equipo: **"Captación de Propiedades"**
2. Crear etapas del pipeline:
   - Nuevo Lead
   - Contactado
   - Visita Programada
   - Evaluación de Propiedad
   - Contrato Firmado
   - Propiedad Activa

### 10.2 Formulario Web → Lead
El formulario de contacto del sitio web puede enviar directamente a CRM:

1. En el editor del sitio web, usar el snippet **"Formulario"**
2. Configurar la acción del formulario: **Crear un Lead/Oportunidad**
3. Mapear campos:
   - Nombre → Nombre del contacto
   - Email → Email
   - Teléfono → Teléfono
   - Mensaje → Descripción
   - Agregar campo custom: "Dirección de la propiedad"
4. Asignar al equipo "Captación de Propiedades"

---

## RESUMEN: Qué se cubre nativamente vs. qué necesita desarrollo

| Funcionalidad | ¿Nativo? | Notas |
|--------------|----------|-------|
| Alquiler por días con pricing | ✅ Sí | `sale_renting` + `website_sale_renting` |
| Reserva online con date picker | ✅ Sí | Incluido en `website_sale_renting` |
| Control de disponibilidad | ✅ Sí | `sale_stock_renting` |
| Catálogo de propiedades web | ✅ Sí | `website_sale` |
| Propiedades en venta | ✅ Parcial | Como productos de servicio, sin flujo inmobiliario |
| Pagos online (Stripe/MP) | ✅ Sí | Proveedores nativos |
| Pagos Bold | ❌ No | Requiere desarrollo custom |
| WhatsApp backend (mensajes) | ✅ Sí | `whatsapp` Enterprise |
| WhatsApp botón flotante web | ❌ No | Desarrollo simple HTML/JS |
| Redes sociales en footer | ✅ Sí | Configuración nativa del sitio web |
| Formulario de contacto | ✅ Sí | Snippet nativo → CRM |
| Captación → CRM | ✅ Sí | Formulario web → Lead |
| Mapa de ubicación | ❌ No | Requiere desarrollo custom |
| Filtro por zona en mapa | ❌ No | Requiere desarrollo custom |
| Sync calendario Airbnb/Booking | ❌ No | Requiere desarrollo custom (iCal) |
| Portal para propietarios (ver) | ✅ Parcial | Solo lectura de órdenes/facturas |
| Portal para propietarios (crear) | ❌ No | Requiere desarrollo custom |
| Páginas web (diseño) | ✅ Sí | Editor de sitio web nativo |
