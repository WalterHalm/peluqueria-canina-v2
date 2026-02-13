# 📋 RESUMEN EJECUTIVO - DEPLOYMENT COMPLETO

## 🎯 Objetivo
Subir ambos módulos a GitHub y desplegarlos en servidor con control total (start/stop/restart).

---

## ✅ CHECKLIST COMPLETO

### FASE 1: GitHub (15 minutos)
- [ ] Crear repositorio `peluqueria_canina` en GitHub
- [ ] Crear repositorio `peluqueria_canina_pro` en GitHub
- [ ] Subir código del módulo base
- [ ] Subir código del módulo PRO
- [ ] Verificar que ambos repositorios están públicos/accesibles

### FASE 2: Servidor Oracle Cloud (20 minutos)
- [ ] Crear cuenta en Oracle Cloud
- [ ] Crear VM Ubuntu (Always Free)
- [ ] Configurar firewall (puerto 8069)
- [ ] Descargar SSH key
- [ ] Conectar por SSH

### FASE 3: Instalación Odoo (30 minutos)
- [ ] Ejecutar script de instalación automática
- [ ] Clonar ambos módulos desde GitHub
- [ ] Configurar odoo.conf
- [ ] Crear servicio systemd
- [ ] Iniciar Odoo

### FASE 4: Configuración (10 minutos)
- [ ] Acceder desde navegador
- [ ] Crear base de datos
- [ ] Instalar módulo base
- [ ] Instalar módulo PRO
- [ ] Cambiar password de admin

### FASE 5: Comandos de Control
- [ ] Probar `sudo systemctl start odoo`
- [ ] Probar `sudo systemctl stop odoo`
- [ ] Probar `sudo systemctl restart odoo`
- [ ] Probar `sudo systemctl status odoo`
- [ ] Probar `sudo journalctl -u odoo -f`

---

## 📝 COMANDOS EXACTOS

### 1. Subir Módulo Base a GitHub
```bash
cd "c:\Program Files\Odoo 19.0.20251002\server\odoo\addons_extras\peluqueria_canina"
git init
git add .
git commit -m "Initial commit - Peluqueria Canina Base"
git remote add origin https://github.com/TU_USUARIO/peluqueria_canina.git
git push -u origin main
```

### 2. Subir Módulo PRO a GitHub
```bash
cd "c:\Program Files\Odoo 19.0.20251002\server\odoo\addons_extras\peluqueria_canina_pro"
git init
git add .
git commit -m "Initial commit - Peluqueria Canina PRO"
git remote add origin https://github.com/TU_USUARIO/peluqueria_canina_pro.git
git push -u origin main
```

### 3. Conectar al Servidor
```bash
ssh -i "ruta/a/ssh-key.key" ubuntu@TU_IP_PUBLICA
```

### 4. Script de Instalación Completo (Copiar TODO)
```bash
#!/bin/bash
# Script de instalación automática de Odoo 19 con módulos Peluquería Canina

echo "======================================"
echo "Instalando Odoo 19 - Peluquería Canina"
echo "======================================"

# Actualizar sistema
echo "1/10 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
echo "2/10 Instalando dependencias..."
sudo apt install -y postgresql python3-pip python3-dev libxml2-dev libxslt1-dev \
    libldap2-dev libsasl2-dev libtiff5-dev libjpeg8-dev libopenjp2-7-dev \
    zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev \
    libfribidi-dev libxcb1-dev libpq-dev git npm nodejs

# Instalar wkhtmltopdf
echo "3/10 Instalando wkhtmltopdf..."
wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo apt install -y ./wkhtmltox_0.12.6.1-2.jammy_amd64.deb
rm wkhtmltox_0.12.6.1-2.jammy_amd64.deb

# Crear usuario Odoo
echo "4/10 Creando usuario Odoo..."
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# Instalar Odoo
echo "5/10 Instalando Odoo 19..."
sudo su - odoo -c "git clone https://github.com/odoo/odoo.git --depth 1 --branch 19.0 /opt/odoo/odoo"
sudo su - odoo -c "pip3 install -r /opt/odoo/odoo/requirements.txt"

# Crear directorios
echo "6/10 Creando directorios..."
sudo mkdir -p /opt/odoo/custom/addons
sudo mkdir -p /var/lib/odoo
sudo mkdir -p /var/log/odoo
sudo mkdir -p /opt/backups/odoo
sudo chown -R odoo:odoo /opt/odoo /var/lib/odoo /var/log/odoo /opt/backups/odoo

# Configurar PostgreSQL
echo "7/10 Configurando PostgreSQL..."
sudo -u postgres createuser -s odoo
sudo -u postgres createdb -O odoo peluqueria_db

# Clonar módulos (REEMPLAZAR TU_USUARIO con tu usuario de GitHub)
echo "8/10 Clonando módulos desde GitHub..."
read -p "Ingresa tu usuario de GitHub: " GITHUB_USER
sudo su - odoo -c "cd /opt/odoo/custom/addons && git clone https://github.com/$GITHUB_USER/peluqueria_canina.git"
sudo su - odoo -c "cd /opt/odoo/custom/addons && git clone https://github.com/$GITHUB_USER/peluqueria_canina_pro.git"

# Crear configuración
echo "9/10 Creando configuración..."
sudo tee /etc/odoo.conf > /dev/null <<EOF
[options]
admin_passwd = Admin2024!Cambiar
db_host = localhost
db_port = 5432
db_user = odoo
db_password = False
db_name = peluqueria_db
addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom/addons/peluqueria_canina,/opt/odoo/custom/addons/peluqueria_canina_pro
data_dir = /var/lib/odoo
logfile = /var/log/odoo/odoo.log
log_level = info
http_port = 8069
workers = 2
max_cron_threads = 1
limit_time_cpu = 60
limit_time_real = 120
EOF

# Crear servicio systemd
echo "10/10 Creando servicio systemd..."
sudo tee /etc/systemd/system/odoo.service > /dev/null <<EOF
[Unit]
Description=Odoo 19 - Peluqueria Canina
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo/odoo-bin -c /etc/odoo.conf
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configurar firewall
echo "Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 8069/tcp
sudo ufw --force enable

# Iniciar Odoo
echo "Iniciando Odoo..."
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo

# Esperar 10 segundos
sleep 10

# Mostrar estado
sudo systemctl status odoo --no-pager

echo ""
echo "======================================"
echo "✅ INSTALACIÓN COMPLETADA"
echo "======================================"
echo ""
echo "📍 Accede a: http://$(curl -s ifconfig.me):8069"
echo ""
echo "🔑 Credenciales iniciales:"
echo "   Usuario: admin"
echo "   Password: admin"
echo ""
echo "⚠️  IMPORTANTE: Cambia el password inmediatamente"
echo ""
echo "📋 Comandos útiles:"
echo "   sudo systemctl start odoo      # Iniciar"
echo "   sudo systemctl stop odoo       # Detener"
echo "   sudo systemctl restart odoo    # Reiniciar"
echo "   sudo systemctl status odoo     # Ver estado"
echo "   sudo journalctl -u odoo -f     # Ver logs en vivo"
echo ""
echo "📂 Rutas importantes:"
echo "   Configuración: /etc/odoo.conf"
echo "   Logs: /var/log/odoo/odoo.log"
echo "   Módulos: /opt/odoo/custom/addons/"
echo ""
echo "======================================"
```

### 5. Comandos de Control Diario
```bash
# Ver estado
sudo systemctl status odoo

# Iniciar servicio
sudo systemctl start odoo

# Detener servicio
sudo systemctl stop odoo

# Reiniciar servicio
sudo systemctl restart odoo

# Ver logs en tiempo real
sudo journalctl -u odoo -f

# Ver últimas 100 líneas de log
sudo journalctl -u odoo -n 100 --no-pager
```

### 6. Actualizar Código desde GitHub
```bash
# Conectar al servidor
ssh -i ssh-key.key ubuntu@TU_IP

# Detener Odoo
sudo systemctl stop odoo

# Actualizar módulo base
cd /opt/odoo/custom/addons/peluqueria_canina
sudo -u odoo git pull

# Actualizar módulo PRO
cd /opt/odoo/custom/addons/peluqueria_canina_pro
sudo -u odoo git pull

# Actualizar módulos en Odoo
sudo -u odoo /opt/odoo/odoo/odoo-bin -c /etc/odoo.conf -d peluqueria_db \
  -u peluqueria_canina,peluqueria_canina_pro --stop-after-init

# Reiniciar Odoo
sudo systemctl start odoo

# Verificar
sudo systemctl status odoo
```

---

## 🔄 WORKFLOW COMPLETO DE DESARROLLO

### En tu PC (Desarrollo Local)
```bash
# 1. Hacer cambios en el código
# ... editar archivos ...

# 2. Probar localmente
# ... verificar que funciona ...

# 3. Commit y push
cd "c:\Program Files\Odoo 19.0.20251002\server\odoo\addons_extras\peluqueria_canina_pro"
git add .
git commit -m "Descripción del cambio"
git push origin main
```

### En el Servidor (Producción)
```bash
# 1. Conectar
ssh -i ssh-key.key ubuntu@TU_IP

# 2. Actualizar
sudo systemctl stop odoo
cd /opt/odoo/custom/addons/peluqueria_canina_pro
sudo -u odoo git pull
sudo systemctl start odoo

# 3. Verificar
sudo journalctl -u odoo -f
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Problema: Odoo no inicia
```bash
# Ver error exacto
sudo journalctl -u odoo -n 50 --no-pager

# Verificar PostgreSQL
sudo systemctl status postgresql
sudo systemctl restart postgresql

# Verificar permisos
sudo chown -R odoo:odoo /opt/odoo /var/lib/odoo /var/log/odoo

# Reintentar
sudo systemctl restart odoo
```

### Problema: No puedo acceder desde el navegador
```bash
# Verificar que Odoo está corriendo
sudo systemctl status odoo

# Verificar puerto
sudo netstat -tlnp | grep 8069

# Verificar firewall local
sudo ufw status

# Verificar Oracle Cloud Security List
# Debe tener regla Ingress para puerto 8069
```

### Problema: Error al actualizar módulo
```bash
# Modo seguro: actualizar sin iniciar
sudo -u odoo /opt/odoo/odoo/odoo-bin -c /etc/odoo.conf -d peluqueria_db \
  -u peluqueria_canina_pro --stop-after-init

# Ver logs
sudo tail -f /var/log/odoo/odoo.log
```

---

## 📊 INFORMACIÓN DEL SISTEMA

### Ver uso de recursos
```bash
# CPU y RAM
htop

# Espacio en disco
df -h

# Procesos de Odoo
ps aux | grep odoo

# Conexiones PostgreSQL
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='peluqueria_db';"
```

### Backup manual
```bash
# Backup de base de datos
sudo -u postgres pg_dump peluqueria_db | gzip > ~/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup de filestore
sudo tar -czf ~/filestore_$(date +%Y%m%d_%H%M%S).tar.gz /var/lib/odoo/filestore

# Descargar a tu PC
# En tu PC:
scp -i ssh-key.key ubuntu@TU_IP:~/backup_*.sql.gz .
```

---

## ✅ VERIFICACIÓN FINAL

Después de completar todo, verifica:

1. ✅ Ambos repositorios en GitHub están actualizados
2. ✅ Puedes acceder a `http://TU_IP:8069`
3. ✅ Los módulos están instalados y funcionando
4. ✅ `sudo systemctl status odoo` muestra "active (running)"
5. ✅ Puedes detener/iniciar/reiniciar el servicio
6. ✅ Los logs se ven correctos: `sudo journalctl -u odoo -f`
7. ✅ Puedes hacer git pull y actualizar

---

**¡Sistema en producción con control completo!** 🎉
