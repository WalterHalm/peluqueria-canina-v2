# E-commerce Ventanas PVC - Odoo 19

## 📋 DESCRIPCIÓN

Sistema completo de e-commerce profesional para venta de ventanas PVC a particulares y distribuidores.

### Características Principales:
✅ Catálogo organizado por series (Económica, Estándar, Premium, Luxury)
✅ Gestión de medidas y características técnicas
✅ Carrito completo con impuestos y envíos
✅ Sistema de testimonios de clientes
✅ Seguimiento de pedidos en tiempo real
✅ Precios diferenciados (particulares/distribuidores)
✅ Diseño profesional responsive
✅ Panel de administración intuitivo

---

## 🚀 INSTALACIÓN

### 1. MÓDULOS NATIVOS ODOO A INSTALAR

Accede a tu base de datos Odoo y activa el modo desarrollador:
`Configuración > Activar modo desarrollador`

Luego instala estos módulos desde `Aplicaciones`:

**OBLIGATORIOS:**
- `website` - Sitio web base
- `website_sale` - Tienda online
- `sale_management` - Gestión de ventas
- `stock` - Inventario
- `delivery` - Gestión de envíos
- `payment` - Pasarela de pagos
- `account` - Contabilidad
- `portal` - Portal de clientes
- `rating` - Valoraciones

**OPCIONALES (Enterprise):**
- `website_enterprise` - Funcionalidades enterprise
- `website_sale_dashboard` - Dashboard de ventas
- `sale_enterprise` - Ventas enterprise
- `website_crm` - Formularios de contacto
- `delivery_fedex` o `delivery_dhl` - Integración transportistas

### 2. INSTALAR MÓDULO PERSONALIZADO

1. El módulo ya está en: `C:\Program Files\Odoo 19.0.20251002\server\odoo\addons_extras\ecommerce_aberturas`

2. Actualiza la lista de aplicaciones:
   - Ve a `Aplicaciones`
   - Click en el menú (☰) superior
   - Click en `Actualizar lista de aplicaciones`
   - Confirma

3. Busca "E-commerce Ventanas PVC" e instálalo

### 3. CONFIGURACIÓN INICIAL

#### A. Configurar Series de Ventanas
Las series ya están precargadas:
- Serie Económica
- Serie Estándar
- Serie Premium
- Serie Luxury

Accede desde: `E-commerce PVC > Catálogo > Series`

#### B. Crear Productos
1. Ve a `E-commerce PVC > Catálogo > Ventanas PVC`
2. Click en `Crear`
3. Completa:
   - Nombre del producto
   - Serie
   - Medidas (ancho x alto)
   - Tipo de vidrio
   - Características técnicas
   - Precio normal
   - Precio distribuidor
   - Subir fotos
   - Adjuntar ficha técnica PDF

#### C. Configurar Tipos de Cliente
Los clientes se clasifican automáticamente en:
- **Particular**: Precio normal
- **Distribuidor**: Precio especial con cantidad mínima

Edita un cliente desde `Contactos` y selecciona el tipo.

#### D. Gestionar Testimonios
1. Ve a `E-commerce PVC > Marketing > Testimonios`
2. Crea testimonios manualmente o espera a que los clientes los envíen
3. Marca como "Publicado" para mostrarlos en el website
4. Marca como "Destacado" para mostrarlos en la homepage

#### E. Configurar Website
1. Ve a `Website > Configuración > Ajustes`
2. Configura:
   - Nombre de la tienda
   - Logo
   - Colores corporativos
   - Métodos de pago
   - Métodos de envío
   - Impuestos

3. Edita la homepage:
   - Ve a `Website > Sitio`
   - Click en `Editar`
   - Arrastra el bloque "Series de Ventanas"
   - Arrastra el bloque "Testimonios de Clientes"

---

## 📊 ESTRUCTURA DE MODELOS

### 1. product.series
- Series de ventanas (Económica, Estándar, Premium, Luxury)
- Nivel de calidad
- Descripción y características

### 2. product.template (heredado)
- Ventanas PVC con características técnicas
- Medidas personalizables
- Tipo de vidrio
- Aislamiento térmico/acústico
- Nivel de seguridad
- Fichas técnicas PDF
- Precios diferenciados

### 3. customer.testimonial
- Testimonios de clientes
- Valoración (1-5 estrellas)
- Foto del cliente
- Compra verificada
- Publicación y destacados

### 4. sale.order (heredado)
- Seguimiento personalizado de pedidos
- Estados: Confirmado > Producción > Calidad > Empaquetado > Enviado > En Tránsito > Entregado
- URL de seguimiento
- Fecha estimada de entrega

### 5. res.partner (heredado)
- Tipo de cliente (Particular/Distribuidor)
- Código de distribuidor
- Tasa de descuento

---

## 🎨 DISEÑO Y PERSONALIZACIÓN

### Colores Profesionales
El diseño usa una paleta sobria y profesional:
- Primary: #2c3e50 (azul oscuro)
- Secondary: #34495e (gris azulado)
- Accent: #3498db (azul brillante)
- Light BG: #ecf0f1 (gris claro)

### Tipografía
- Fuente: Roboto, Helvetica Neue, Arial
- Limpia y legible
- Optimizada para web

### Responsive
- Totalmente adaptado a móviles
- Diseño mobile-first
- Optimizado para tablets

---

## 🔧 FUNCIONALIDADES AVANZADAS

### Portal del Cliente
Los clientes pueden:
- Ver sus pedidos
- Seguimiento en tiempo real
- Descargar facturas
- Dejar testimonios

### Precios Dinámicos
- Precio normal para particulares
- Precio especial para distribuidores (con cantidad mínima)
- Descuentos por volumen configurables

### SEO Optimizado
- URLs amigables
- Meta tags automáticos
- Sitemap XML
- Imágenes optimizadas

---

## 📈 PRÓXIMAS MEJORAS SUGERIDAS

1. **Configurador 3D**: Visualización de ventanas en tiempo real
2. **Chat en vivo**: Soporte instantáneo
3. **Calculadora de medidas**: Ayuda al cliente a medir
4. **Blog**: Contenido sobre ventanas PVC
5. **Comparador de productos**: Comparar series
6. **Wishlist**: Lista de deseos
7. **Programa de referidos**: Descuentos por recomendaciones

---

## 🆘 SOPORTE

Para soporte técnico o consultas:
- Email: soporte@tuempresa.com
- Teléfono: +XX XXX XXX XXX
- Website: https://www.tuempresa.com

---

## 📝 LICENCIA

LGPL-3

---

## 👨‍💻 AUTOR

Tu Empresa - Especialistas en Ventanas PVC
