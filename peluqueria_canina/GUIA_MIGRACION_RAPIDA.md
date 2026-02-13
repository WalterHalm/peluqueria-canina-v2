# Guía de Migración: Odoo 17 → Odoo 19
## Peluquería Canina

### Requisitos Previos
- Base de datos Odoo 17 operativa
- Base de datos Odoo 19 nueva (limpia)
- Módulo `peluqueria_canina` instalado en Odoo 19
- Acceso a PostgreSQL (puerto 5433)
- Python 3 con psycopg2

### Estructura del Modelo

**Mascota** (`peluqueria.mascota`):
- Campos principales: name, fecha_nacimiento, edad (computed), raza, color, medida, peso
- Relación: `owner_id` → `res.partner`
- Imagen: `image` (Binary field con `attachment=True`)
- Hereda: `mail.thread`, `mail.activity.mixin`, `image.mixin`

**Personas** (extiende `res.partner`):
- Campo: `pet_ids` (One2many a mascotas)

### Proceso de Migración

#### Paso 1: Validación Pre-Migración
```bash
python c:\temp\validar_pre_migracion.py
```
Verifica:
- Integridad de datos en BD origen
- Existencia de archivos en filestore
- Relaciones válidas entre tablas

#### Paso 2: Ejecutar Migración
```bash
python c:\temp\migracion_definitiva.py
```

**Qué migra:**
1. **Clientes** (`res_partner`): ID > 10, con active=TRUE y DNI type
2. **Mascotas** (`peluqueria_mascota`): Todos los campos excepto imagen
3. **Attachments** (`ir_attachment`): Con res_field='image', sin especificar ID (auto-increment)
4. **Filestore**: Copia archivos desde BD origen a BD destino

**Validación Post-Migración automática:**
- Cuenta registros migrados vs origen
- Verifica relaciones owner_id
- Confirma existencia de archivos en filestore

### Configuración de Base de Datos

**BD Origen:**
- Nombre: `peluqueria_canina_19`
- Puerto: 5433
- Filestore: `c:\users\ingenio 2\appdata\local\openerp s.a\odoo\filestore\peluqueria_canina_19`

**BD Destino:**
- Nombre: `peluqueria_nueva`
- Puerto: 5433
- Filestore: `c:\users\ingenio 2\appdata\local\openerp s.a\odoo\filestore\peluqueria_nueva`

### Puntos Clave

1. **Imágenes en Odoo 19:**
   - Usar `fields.Binary("Imagen", attachment=True)`
   - NO usar `fields.Image` con campos relacionados
   - Los datos se guardan en `ir_attachment`, no en la columna de la tabla

2. **IDs de Attachments:**
   - NO copiar IDs de attachments (pueden existir conflictos)
   - Dejar que PostgreSQL genere IDs automáticamente

3. **Clientes:**
   - Filtrar ID > 10 para evitar usuarios del sistema
   - Establecer `active=TRUE` y `l10n_latam_identification_type_id=4` (DNI)

4. **Filestore:**
   - Los archivos ya existen, solo verificar que estén accesibles
   - Estructura: `XX/XXXXXXX...` (primeros 2 chars = directorio)

### Solución de Problemas

**Imágenes no se visualizan:**
- Verificar que exista registro en `ir_attachment` con `res_field='image'`
- Confirmar que archivo existe en filestore
- Verificar que campo del modelo sea `Binary(attachment=True)`

**Error de foreign key en attachments:**
- Usar `create_uid=2` y `write_uid=2` (usuario admin)

**Columnas faltantes:**
- Actualizar módulo: `odoo-bin -u peluqueria_canina -d peluqueria_nueva --stop-after-init`

### Archivos Importantes

- `migration/migracion_definitiva.py` - Script principal de migración
- `migration/validar_pre_migracion.py` - Validación de datos
- `migration/limpiar_datos.py` - Limpieza de datos de prueba

### Resultado Esperado

- ✓ 809 clientes
- ✓ 513 mascotas
- ✓ 491 imágenes
- ✓ 22 mascotas sin imagen (normal)
- ✓ Todas las relaciones válidas
- ✓ Todos los archivos en filestore

---
**Fecha:** Febrero 2026  
**Versión Origen:** Odoo 17  
**Versión Destino:** Odoo 19.0.20251002
