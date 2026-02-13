# 🏗️ ARQUITECTURA DE SOFTWARE Y DEPLOYMENT

## 📋 ÍNDICE
1. [Mejores Prácticas de Arquitectura](#mejores-prácticas)
2. [Limpieza de Código Realizada](#limpieza-realizada)
3. [Opciones de Hosting Gratuito](#hosting-gratuito)
4. [Deployment Paso a Paso](#deployment)
5. [Seguridad y Mantenimiento](#seguridad)

---

## 🎯 MEJORES PRÁCTICAS DE ARQUITECTURA

### 1. ESTRUCTURA DE MÓDULOS ODOO

#### ✅ Organización de Archivos
```
peluqueria_canina_pro/
├── __init__.py                 # Importa models, controllers, wizards
├── __manifest__.py             # Metadatos del módulo
├── models/
│   ├── __init__.py            # Importa todos los modelos
│   ├── servicio.py            # Un modelo por archivo
│   ├── turno.py
│   ├── visita.py
│   ├── mascota.py
│   └── dashboard.py
├── views/
│   ├── servicio_views.xml     # Vistas agrupadas por modelo
│   ├── turno_views.xml
│   ├── visita_views.xml
│   └── menu_views.xml         # Menús separados
├── security/
│   └── ir.model.access.csv    # Permisos de acceso
├── data/
│   └── servicio_data.xml      # Datos iniciales
├── static/
│   └── src/
│       └── css/
│           └── dashboard.css  # Estilos personalizados
└── reports/                    # Reportes (futuro)
```

#### ✅ Convenciones de Nombres
- **Modelos**: `peluqueria.nombre` (snake_case)
- **Clases Python**: `NombreModelo` (PascalCase)
- **Métodos**: `action_nombre`, `_compute_campo` (snake_case)
- **Campos**: `campo_nombre` (snake_case)
- **XML IDs**: `view_modelo_tipo`, `action_modelo` (snake_case)

---

### 2. PRINCIPIOS SOLID EN ODOO

#### Single Responsibility (Responsabilidad Única)
✅ **Correcto**: Cada modelo tiene una responsabilidad clara
- `servicio.py` → Gestión de servicios
- `turno.py` → Gestión de turnos
- `visita.py` → Gestión de visitas

❌ **Incorrecto**: Un modelo que hace todo

#### Open/Closed (Abierto/Cerrado)
✅ **Correcto**: Usar herencia para extender
```python
class Mascota(models.Model):
    _inherit = 'peluqueria.mascota'  # Extiende sin modificar
    turno_ids = fields.One2many(...)
```

#### Liskov Substitution (Sustitución de Liskov)
✅ **Correcto**: Los métodos heredados funcionan igual
```python
def action_confirmar(self):
    # Comportamiento consistente en todos los estados
    self.write({'state': 'confirmado'})
```

#### Interface Segregation (Segregación de Interfaces)
✅ **Correcto**: Mixins específicos
```python
_inherit = ['mail.thread', 'mail.activity.mixin']  # Solo lo necesario
```

#### Dependency Inversion (Inversión de Dependencias)
✅ **Correcto**: Depender de abstracciones
```python
empleado_id = fields.Many2one('res.users')  # Modelo estándar de Odoo
```

---

### 3. PATRONES DE DISEÑO EN ODOO

#### Patrón MVC (Model-View-Controller)
- **Model**: `models/*.py` (Lógica de negocio)
- **View**: `views/*.xml` (Interfaz de usuario)
- **Controller**: Odoo maneja automáticamente

#### Patrón Repository
```python
# Odoo implementa Repository Pattern automáticamente
turnos = self.env['peluqueria.turno'].search([('state', '=', 'confirmado')])
```

#### Patrón Observer
```python
# Tracking automático de cambios
state = fields.Selection(..., tracking=True)
```

#### Patrón Factory
```python
# create() es un Factory Method
visita = self.env['peluqueria.visita'].create({...})
```

---

### 4. CÓDIGO LIMPIO (Clean Code)

#### ✅ Nombres Descriptivos
```python
# BIEN
def _compute_ganancia(self):
    for record in self:
        record.ganancia = record.total_venta - record.costo_total

# MAL
def calc(self):
    for r in self:
        r.g = r.tv - r.ct
```

#### ✅ Funciones Pequeñas
```python
# BIEN - Una responsabilidad
def action_confirmar(self):
    self.write({'state': 'confirmado'})
    return True

# MAL - Múltiples responsabilidades
def action_confirmar(self):
    self.write({'state': 'confirmado'})
    self.send_email()
    self.update_calendar()
    self.notify_users()
```

#### ✅ DRY (Don't Repeat Yourself)
```python
# BIEN - Reutilizar código
@api.depends('precio', 'costo')
def _compute_margen(self):
    for record in self:
        if record.precio:
            record.margen = ((record.precio - record.costo) / record.precio) * 100

# MAL - Código duplicado en múltiples lugares
```

#### ✅ Comentarios Útiles
```python
# BIEN - Explica el "por qué"
# Multiplicamos por 100 porque el campo no usa widget percentage
record.margen = ((precio - costo) / precio) * 100

# MAL - Explica el "qué" (obvio)
# Asigna el margen
record.margen = margen
```

---

## 🧹 LIMPIEZA DE CÓDIGO REALIZADA

### Problemas Encontrados y Solucionados

#### 1. Método Duplicado en turno.py
```python
# ANTES - action_no_asistio() aparecía 2 veces
def action_no_asistio(self):  # Línea 215
    ...
def action_no_asistio(self):  # Línea 265 (DUPLICADO)
    ...

# DESPUÉS - Solo una vez
def action_no_asistio(self):
    self.write({'state': 'no_asistio'})
    return True
```

#### 2. Métodos No Utilizados Eliminados
```python
# ELIMINADOS (no se usan en las vistas)
def action_cancelar(self):  # Wizard no implementado
def action_ver_visita(self):  # No se usa en UI
```

#### 3. Archivo historial.py Eliminado
- Modelo innecesario (se usa domain en visita)
- Causaba SyntaxError
- Removido del `__init__.py`

---

## 🌐 OPCIONES DE HOSTING GRATUITO

### Opción 1: PythonAnywhere (RECOMENDADO)
**Características:**
- ✅ Gratuito hasta 512MB RAM
- ✅ Python preinstalado
- ✅ PostgreSQL incluido
- ✅ Dominio: `tuusuario.pythonanywhere.com`
- ✅ HTTPS automático
- ❌ Limitación: 1 app web

**Pasos:**
1. Crear cuenta en https://www.pythonanywhere.com
2. Subir código Odoo
3. Configurar PostgreSQL
4. Configurar Web App con WSGI

**Costo Upgrade:** $5/mes (más recursos)

---

### Opción 2: Render.com
**Características:**
- ✅ 750 horas/mes gratis
- ✅ PostgreSQL gratuito (90 días)
- ✅ Deploy desde GitHub
- ✅ HTTPS automático
- ❌ Se duerme después de 15 min inactividad

**Pasos:**
1. Crear cuenta en https://render.com
2. Conectar repositorio GitHub
3. Configurar como Web Service
4. Agregar PostgreSQL database

**Costo Upgrade:** $7/mes (siempre activo)

---

### Opción 3: Railway.app
**Características:**
- ✅ $5 crédito mensual gratis
- ✅ PostgreSQL incluido
- ✅ Deploy desde GitHub
- ✅ HTTPS automático
- ✅ No se duerme

**Pasos:**
1. Crear cuenta en https://railway.app
2. New Project → Deploy from GitHub
3. Agregar PostgreSQL
4. Configurar variables de entorno

**Costo Upgrade:** Pay as you go (~$10-20/mes)

---

### Opción 4: Heroku (Limitado)
**Características:**
- ✅ Dyno gratuito (550 horas/mes)
- ✅ PostgreSQL gratuito (10K filas)
- ✅ Deploy desde Git
- ❌ Se duerme después de 30 min
- ❌ Limitaciones estrictas

**Pasos:**
1. Crear cuenta en https://heroku.com
2. Instalar Heroku CLI
3. `heroku create nombre-app`
4. `git push heroku main`

**Costo Upgrade:** $7/mes por dyno

---

### Opción 5: VPS Gratuito (Oracle Cloud)
**Características:**
- ✅ GRATIS PERMANENTE
- ✅ 1 GB RAM, 1 CPU
- ✅ 200 GB almacenamiento
- ✅ IP pública
- ✅ Control total
- ❌ Requiere configuración manual

**Pasos:**
1. Crear cuenta en https://cloud.oracle.com
2. Crear VM (Always Free tier)
3. Instalar Ubuntu
4. Instalar Odoo manualmente
5. Configurar firewall y dominio

**Costo:** $0 (permanente)

---

## 🚀 DEPLOYMENT PASO A PASO

### Preparación del Código

#### 1. Crear requirements.txt
```txt
odoo==19.0
psycopg2-binary==2.9.9
```

#### 2. Crear .gitignore
```
__pycache__/
*.pyc
*.pyo
*.log
filestore/
sessions/
.vscode/
```

#### 3. Crear odoo.conf
```ini
[options]
admin_passwd = CAMBIAR_ESTO
db_host = localhost
db_port = 5432
db_user = odoo
db_password = TU_PASSWORD
addons_path = /ruta/a/addons,/ruta/a/peluqueria_canina_pro
http_port = 8069
```

---

### Deployment en PythonAnywhere (Paso a Paso)

#### Paso 1: Crear Cuenta
1. Ir a https://www.pythonanywhere.com
2. Sign up (gratis)
3. Verificar email

#### Paso 2: Subir Código
```bash
# En tu PC local
zip -r peluqueria_canina_pro.zip peluqueria_canina_pro/

# En PythonAnywhere Console
cd ~
wget URL_DE_TU_ZIP
unzip peluqueria_canina_pro.zip
```

#### Paso 3: Instalar Dependencias
```bash
pip3 install --user odoo psycopg2-binary
```

#### Paso 4: Configurar PostgreSQL
```bash
# En PythonAnywhere Console
createdb peluqueria_db
```

#### Paso 5: Configurar Web App
1. Web → Add a new web app
2. Manual configuration → Python 3.10
3. Editar WSGI file:
```python
import sys
path = '/home/tuusuario/odoo'
if path not in sys.path:
    sys.path.append(path)

from odoo import http
application = http.root
```

#### Paso 6: Iniciar Odoo
```bash
python3 odoo-bin -c odoo.conf -d peluqueria_db -i peluqueria_canina_pro
```

#### Paso 7: Acceder
- URL: `https://tuusuario.pythonanywhere.com`
- Usuario: admin
- Password: admin (cambiar inmediatamente)

---

### Deployment en Railway (Más Fácil)

#### Paso 1: Preparar GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tuusuario/peluqueria.git
git push -u origin main
```

#### Paso 2: Crear Proyecto en Railway
1. Ir a https://railway.app
2. New Project → Deploy from GitHub
3. Seleccionar repositorio

#### Paso 3: Agregar PostgreSQL
1. New → Database → PostgreSQL
2. Copiar DATABASE_URL

#### Paso 4: Configurar Variables
```
ODOO_ADMIN_PASSWORD=tu_password_seguro
DATABASE_URL=postgresql://...
PORT=8069
```

#### Paso 5: Deploy Automático
- Railway detecta cambios en GitHub
- Deploy automático en cada push

---

## 🔒 SEGURIDAD Y MANTENIMIENTO

### Checklist de Seguridad

#### ✅ Antes de Subir a Producción
- [ ] Cambiar admin_passwd en odoo.conf
- [ ] Usar contraseñas fuertes
- [ ] Habilitar HTTPS (SSL)
- [ ] Configurar firewall
- [ ] Limitar acceso a PostgreSQL
- [ ] Hacer backup de base de datos
- [ ] Configurar logs
- [ ] Deshabilitar modo debug

#### ✅ Configuración Segura
```ini
[options]
admin_passwd = PASSWORD_COMPLEJO_AQUI
db_host = localhost  # No exponer públicamente
db_port = 5432
limit_time_cpu = 60
limit_time_real = 120
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
workers = 2
max_cron_threads = 1
```

---

### Mantenimiento Regular

#### Backups Automáticos
```bash
# Crear script backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump peluqueria_db > backup_$DATE.sql
# Subir a cloud storage
```

#### Monitoreo
- Logs: `/var/log/odoo/`
- Uso de recursos: `htop`
- Base de datos: `pg_stat_activity`

#### Actualizaciones
```bash
# Actualizar módulo
odoo-bin -c odoo.conf -d peluqueria_db -u peluqueria_canina_pro
```

---

## 📊 COMPARACIÓN DE OPCIONES

| Característica | PythonAnywhere | Render | Railway | Oracle Cloud |
|----------------|----------------|--------|---------|--------------|
| **Costo Inicial** | Gratis | Gratis | $5/mes | Gratis |
| **Facilidad** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Recursos** | 512MB RAM | 512MB RAM | 1GB RAM | 1GB RAM |
| **Uptime** | 100% | 85% (duerme) | 100% | 100% |
| **PostgreSQL** | Incluido | 90 días | Incluido | Manual |
| **HTTPS** | ✅ | ✅ | ✅ | Manual |
| **Dominio** | Subdominio | Subdominio | Subdominio | IP pública |
| **Escalabilidad** | Limitada | Buena | Excelente | Total |

---

## 🎯 RECOMENDACIÓN FINAL

### Para Empezar (Gratis)
1. **Railway.app** - Más fácil, mejor experiencia
2. **Oracle Cloud** - Si sabes Linux, gratis permanente

### Para Producción (Pago)
1. **Railway** - $10-20/mes, excelente
2. **DigitalOcean** - $6/mes, VPS completo
3. **AWS Lightsail** - $5/mes, escalable

---

## 📚 RECURSOS ADICIONALES

### Documentación
- Odoo: https://www.odoo.com/documentation/19.0/
- PostgreSQL: https://www.postgresql.org/docs/
- Python: https://docs.python.org/3/

### Comunidad
- Odoo Forum: https://www.odoo.com/forum
- Stack Overflow: https://stackoverflow.com/questions/tagged/odoo
- GitHub: https://github.com/odoo/odoo

---

**Última actualización:** 2026-02-13  
**Versión del módulo:** 19.0.2.1
