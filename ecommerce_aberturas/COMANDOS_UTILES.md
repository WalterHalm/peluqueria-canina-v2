# 🛠️ COMANDOS ÚTILES - ADMINISTRACIÓN

## 🔄 ACTUALIZAR EL MÓDULO

Después de hacer cambios en el código:

```bash
# Opción 1: Desde la interfaz
1. Ve a Aplicaciones
2. Busca "E-commerce Ventanas PVC"
3. Click en los 3 puntos (...)
4. Click en "Actualizar"

# Opción 2: Desde línea de comandos
cd "C:\Program Files\Odoo 19.0.20251002\server"
python odoo-bin -u ecommerce_aberturas -d TU_BASE_DE_DATOS
```

---

## 🗄️ BACKUP DE LA BASE DE DATOS

```bash
# Desde la interfaz
1. Ve a Configuración > Base de datos
2. Click en "Gestionar bases de datos"
3. Click en "Backup"
4. Descarga el archivo .zip

# Desde línea de comandos (PostgreSQL)
pg_dump -U odoo -d TU_BASE_DE_DATOS > backup.sql
```

---

## 🔍 VER LOGS DE ERRORES

```bash
# Ubicación de logs
C:\Program Files\Odoo 19.0.20251002\server\odoo.log

# Ver logs en tiempo real (PowerShell)
Get-Content "C:\Program Files\Odoo 19.0.20251002\server\odoo.log" -Wait -Tail 50

# Desde la interfaz
1. Activa modo desarrollador
2. Ve a Configuración > Técnico > Logs
```

---

## 🧹 LIMPIAR CACHE

```bash
# Limpiar assets
1. Ve a Configuración > Técnico > Assets
2. Click en "Regenerar Assets"

# Limpiar cache del navegador
Ctrl + Shift + Delete (Chrome/Edge)
Cmd + Shift + Delete (Mac)
```

---

## 📊 IMPORTAR DATOS MASIVOS

### Importar Productos desde CSV

```csv
# Formato del CSV (productos.csv)
name,series_id/code,width,height,glass_type,list_price,price_distributor
Ventana Premium 120x150,PREM,120,150,double,450.00,350.00
Ventana Luxury 150x180,LUX,150,180,triple,650.00,500.00
```

```bash
# Importar desde la interfaz
1. Ve a E-commerce PVC > Catálogo > Ventanas PVC
2. Click en Favoritos > Importar registros
3. Sube el archivo CSV
4. Mapea los campos
5. Click en Importar
```

### Importar Testimonios desde CSV

```csv
# Formato del CSV (testimonios.csv)
name,email,testimonial,rating,published,featured
Juan Pérez,juan@email.com,Excelente calidad de ventanas,5,True,True
María García,maria@email.com,Muy satisfecha con la compra,5,True,False
```

---

## 🔐 GESTIÓN DE USUARIOS

### Crear Usuario Administrador

```bash
# Desde la interfaz
1. Ve a Configuración > Usuarios y Compañías > Usuarios
2. Click en Crear
3. Completa datos
4. Asigna grupo "Administración / Configuración"

# Cambiar contraseña
1. Edita el usuario
2. Click en "Cambiar contraseña"
```

### Permisos por Rol

```
Administrador: Acceso total
Vendedor: Ver y crear pedidos, productos
Marketing: Gestionar testimonios, contenido
Almacén: Gestionar stock, envíos
```

---

## 🌐 CONFIGURACIÓN DE DOMINIO

### Configurar Dominio Personalizado

```bash
# 1. Configurar DNS (en tu proveedor de dominio)
Tipo: A
Nombre: @
Valor: IP_DE_TU_SERVIDOR

Tipo: CNAME
Nombre: www
Valor: tudominio.com

# 2. Configurar en Odoo
1. Ve a Configuración > Técnico > Parámetros del sistema
2. Busca "web.base.url"
3. Cambia a: https://tudominio.com

# 3. Configurar SSL (Let's Encrypt)
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

---

## 📧 CONFIGURACIÓN DE EMAIL

### Servidor de Correo Saliente (SMTP)

```bash
# Gmail
1. Ve a Configuración > Técnico > Correo saliente
2. Click en Crear
3. Completa:
   - Servidor SMTP: smtp.gmail.com
   - Puerto: 587
   - Seguridad: TLS
   - Usuario: tu-email@gmail.com
   - Contraseña: contraseña-de-aplicación

# Outlook
   - Servidor SMTP: smtp.office365.com
   - Puerto: 587
   - Seguridad: STARTTLS
```

### Servidor de Correo Entrante (IMAP)

```bash
1. Ve a Configuración > Técnico > Correo entrante
2. Click en Crear
3. Completa según tu proveedor
4. Click en "Probar y confirmar"
```

---

## 🎨 PERSONALIZACIÓN DE DISEÑO

### Cambiar Colores del Website

```bash
# Desde el editor
1. Ve a Website > Sitio
2. Click en Editar
3. Click en el icono de paleta (arriba)
4. Personaliza colores

# Desde CSS (avanzado)
Edita: static/src/css/style.css
```

### Cambiar Logo

```bash
1. Ve a Configuración > Compañías
2. Edita tu compañía
3. Sube nuevo logo
4. Guarda
```

---

## 📈 REPORTES Y ESTADÍSTICAS

### Exportar Reporte de Ventas

```bash
1. Ve a Ventas > Reportes > Ventas
2. Selecciona filtros (fecha, producto, etc.)
3. Click en Favoritos > Exportar todo
4. Elige formato (Excel, CSV, PDF)
```

### Dashboard Personalizado

```bash
1. Ve a Dashboard (si tienes website_sale_dashboard)
2. Verás métricas en tiempo real:
   - Ventas del día/mes
   - Productos más vendidos
   - Tasa de conversión
   - Abandono de carrito
```

---

## 🔧 MANTENIMIENTO

### Optimizar Base de Datos

```sql
-- Ejecutar en PostgreSQL
VACUUM ANALYZE;
REINDEX DATABASE TU_BASE_DE_DATOS;
```

### Limpiar Datos Antiguos

```bash
# Desde la interfaz
1. Ve a Configuración > Técnico > Acciones programadas
2. Busca "Limpiar datos antiguos"
3. Configura frecuencia
```

---

## 🐛 DEBUGGING

### Activar Modo Debug

```bash
# Método 1: URL
Agrega ?debug=1 a la URL
Ejemplo: http://localhost:8069/web?debug=1

# Método 2: Interfaz
1. Ve a Configuración
2. Click en "Activar modo desarrollador"

# Método 3: Avanzado
Agrega ?debug=assets a la URL para debug de assets
```

### Ver Queries SQL

```bash
# En el archivo de configuración (odoo.conf)
[options]
log_level = debug_sql
```

---

## 🚀 OPTIMIZACIÓN DE RENDIMIENTO

### Activar Cache

```bash
# En odoo.conf
[options]
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
```

### Optimizar Imágenes

```bash
# Instalar módulo de optimización
1. Busca "Image Optimization" en Apps
2. Instala
3. Configura compresión automática
```

---

## 📱 TESTING MÓVIL

### Probar en Diferentes Dispositivos

```bash
# Chrome DevTools
1. F12 para abrir DevTools
2. Ctrl + Shift + M para modo responsive
3. Selecciona dispositivo (iPhone, iPad, etc.)

# Herramientas online
- BrowserStack: https://www.browserstack.com
- LambdaTest: https://www.lambdatest.com
```

---

## 🔒 SEGURIDAD

### Cambiar Contraseña de Admin

```bash
# Desde línea de comandos
cd "C:\Program Files\Odoo 19.0.20251002\server"
python odoo-bin shell -d TU_BASE_DE_DATOS
>>> env['res.users'].browse(2).write({'password': 'nueva_contraseña'})
>>> env.cr.commit()
```

### Activar 2FA (Autenticación de 2 Factores)

```bash
1. Ve a Configuración > Usuarios
2. Edita tu usuario
3. Activa "Autenticación de dos factores"
4. Escanea QR con Google Authenticator
```

---

## 📞 SOPORTE

### Logs Importantes

```bash
# Ubicaciones
Logs de Odoo: C:\Program Files\Odoo 19.0.20251002\server\odoo.log
Logs de PostgreSQL: C:\Program Files\PostgreSQL\XX\data\log\
Logs de Nginx: C:\nginx\logs\error.log
```

### Información del Sistema

```bash
# Desde la interfaz
1. Ve a Configuración > Técnico > Información del servidor
2. Verás:
   - Versión de Odoo
   - Versión de Python
   - Versión de PostgreSQL
   - Módulos instalados
```

---

## ✅ CHECKLIST DE MANTENIMIENTO MENSUAL

- [ ] Backup de base de datos
- [ ] Actualizar módulos
- [ ] Revisar logs de errores
- [ ] Optimizar base de datos
- [ ] Revisar espacio en disco
- [ ] Actualizar contenido (productos, testimonios)
- [ ] Revisar métricas de ventas
- [ ] Probar funcionalidades críticas

---

**¡Mantén tu e-commerce funcionando perfectamente!** 🚀
