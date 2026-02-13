#!/bin/bash
# Script de Backup Automático para Peluquería Canina PRO

# Configuración
BACKUP_DIR="/opt/backups/odoo"
DB_NAME="peluqueria_db"
FILESTORE_DIR="/var/lib/odoo/filestore"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

# Backup de Base de Datos
echo "Iniciando backup de base de datos..."
sudo -u postgres pg_dump $DB_NAME | gzip > $BACKUP_DIR/db_${DB_NAME}_${DATE}.sql.gz

# Backup de Filestore
echo "Iniciando backup de filestore..."
tar -czf $BACKUP_DIR/filestore_${DATE}.tar.gz $FILESTORE_DIR

# Eliminar backups antiguos
echo "Eliminando backups antiguos (más de $RETENTION_DAYS días)..."
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "filestore_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completado: $DATE"
echo "Archivos:"
ls -lh $BACKUP_DIR/*${DATE}*
