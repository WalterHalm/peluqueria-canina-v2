# 🚀 GUÍA RÁPIDA - SUBIR A GITHUB Y DEPLOYMENT

## PASO 1: Preparar GitHub (10 minutos)

### 1.1 Crear DOS Repositorios en GitHub

#### Repositorio 1: Módulo Base
1. Ve a https://github.com
2. Click en "New repository"
3. Nombre: `peluqueria_canina`
4. Descripción: "Módulo base de gestión para peluquerías caninas - Odoo 19"
5. Público o Privado (tu elección)
6. **NO** marcar "Initialize with README"
7. Click "Create repository"
8. **Copiar la URL**: `https://github.com/TU_USUARIO/peluqueria_canina.git`

#### Repositorio 2: Módulo PRO
1. Click en "New repository" nuevamente
2. Nombre: `peluqueria_canina_pro`
3. Descripción: "Módulo PRO con turnos, visitas y centro de costos - Odoo 19"
4. Público o Privado (tu elección)
5. **NO** marcar "Initialize with README"
6. Click "Create repository"
7. **Copiar la URL**: `https://github.com/TU_USUARIO/peluqueria_canina_pro.git`

### 1.2 Subir Código del Módulo Base
```bash
# Abrir terminal en la carpeta del módulo base
cd "c:\Program Files\Odoo 19.0.20251002\server\odoo\addons_extras\peluqueria_canina"

# Inicializar Git
git init

# Agregar archivos
git add .

# Primer commit
git commit -m "Initial commit - Peluqueria Canina Base v19.0"

# Conectar con GitHub (reemplazar TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/peluqueria_canina.git

# Subir código
git push -u origin main
```

### 1.3 Subir Código del Módulo PRO
```bash
# Abrir terminal en la carpeta del módulo PRO
cd "c:\Program Files\Odoo 19.0.20251002\server\odoo\addons_extras\peluqueria_canina_pro"

# Inicializar Git
git init

# Agregar archivos
git add .

# Primer commit
git commit -m "Initial commit - Peluqueria Canina PRO v19.0.2.1"

# Conectar con GitHub (reemplazar TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/peluqueria_canina_pro.git

# Subir código
git push -u origin main
```

**Nota:** Si pide credenciales, usa **Personal Access Token**:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → Marcar "repo" → Generate
3. Copiar token y usarlo como password

---

## PASO 2: Crear Servidor en Oracle Cloud (15 minutos)

### 2.1 Crear Cuenta
1. Ve a https://cloud.oracle.com
2. Click "Start for free"
3. Completar registro (requiere tarjeta, pero NO cobra)
4. Verificar email

### 2.2 Crear VM (Always Free)
1. Login en Oracle Cloud
2. Menu → Compute → Instances
3. Click "Create Instance"
4. Configuración:
   - Name: `odoo-peluqueria`
   - Image: **Ubuntu 22.04**
   - Shape: **VM.Standard.E2.1.Micro** (Always Free)
   - Network: Default
   - SSH Keys: **Generate a key pair** → Download private key
5. Click "Create"
6. Esperar 2-3 minutos
7. Copiar **Public IP Address**

### 2.3 Configurar Firewall
1. En la instancia → Subnet → Security List
2. Add Ingress Rule:
   - Source CIDR: `0.0.0.0/0`
   - Destination Port: `8069`
   - Description: `Odoo`
3. Save

---

## PASO 3: Conectar por SSH (2 minutos)

### Windows (PowerShell)
```powershell
# Dar permisos a la key
icacls "C:\Users\TU_USUARIO\Downloads\ssh-key.key" /inheritance:r /grant:r "%USERNAME%:R"

# Conectar
ssh -i "C:\Users\TU_USUARIO\Downloads\ssh-key.key" ubuntu@TU_IP_PUBLICA
```

### Linux/Mac
```bash
chmod 400 ~/Downloads/ssh-key.key
ssh -i ~/Downloads/ssh-key.key ubuntu@TU_IP_PUBLICA
```

---

## PASO 4: Instalar Odoo (30 minutos)

### 4.1 Script de Instalación Automática
```bash
# Copiar y pegar TODO este bloque en el servidor

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y postgresql python3-pip python3-dev libxml2-dev libxslt1-dev \
    libldap2-dev libsasl2-dev libtiff5-dev libjpeg8-dev libopenjp2-7-dev \
    zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev \
    libfribidi-dev libxcb1-dev libpq-dev git npm nodejs

# Instalar wkhtmltopdf (para PDFs)
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo apt install -y ./wkhtmltox_0.12.6.1-2.jammy_amd64.deb
rm wkhtmltox_0.12.6.1-2.jammy_amd64.deb

# Crear usuario Odoo
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# Instalar Odoo
sudo su - odoo -c "git clone https://github.com/odoo/odoo.git --depth 1 --branch 19.0 /opt/odoo/odoo"
sudo su - odoo -c "pip3 install -r /opt/odoo/odoo/requirements.txt"

# Crear directorios
sudo mkdir -p /opt/odoo/custom/addons
sudo mkdir -p /var/lib/odoo
sudo mkdir -p /var/log/odoo
sudo chown -R odoo:odoo /opt/odoo /var/lib/odoo /var/log/odoo

# Configurar PostgreSQL
sudo -u postgres createuser -s odoo
sudo -u postgres createdb -O odoo peluqueria_db

# Clonar módulos (REEMPLAZAR TU_USUARIO)
sudo su - odoo -c "cd /opt/odoo/custom/addons && git clone https://github.com/TU_USUARIO/peluqueria_canina.git"
sudo su - odoo -c "cd /opt/odoo/custom/addons && git clone https://github.com/TU_USUARIO/peluqueria_canina_pro.git"

# Crear configuración
sudo tee /etc/odoo.conf > /dev/null <<EOF
[options]
admin_passwd = admin123CAMBIAR
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
EOF

# Crear servicio systemd
sudo tee /etc/systemd/system/odoo.service > /dev/null <<EOF
[Unit]
Description=Odoo 19
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
sudo ufw allow 22/tcp
sudo ufw allow 8069/tcp
sudo ufw --force enable

# Iniciar Odoo
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo

echo "======================================"
echo "✅ INSTALACIÓN COMPLETADA"
echo "======================================"
echo "Accede a: http://TU_IP_PUBLICA:8069"
echo "Usuario: admin"
echo "Password: admin"
echo ""
echo "Comandos útiles:"
echo "  sudo systemctl status odoo    # Ver estado"
echo "  sudo systemctl restart odoo   # Reiniciar"
echo "  sudo journalctl -u odoo -f    # Ver logs"
echo "======================================"
```

---

## PASO 5: Acceder y Configurar (5 minutos)

1. Abrir navegador: `http://TU_IP_PUBLICA:8069`
2. Crear base de datos:
   - Master Password: `admin123CAMBIAR`
   - Database Name: `peluqueria_db`
   - Email: tu@email.com
   - Password: tu_password
   - Language: Spanish
   - Country: Argentina
3. Instalar módulos:
   - Apps → Buscar "peluqueria_canina"
   - Instalar "Peluquería Canina"
   - Instalar "Peluquería Canina PRO"

---

## 📋 COMANDOS ESENCIALES

### Control del Servicio
```bash
# Iniciar
sudo systemctl start odoo

# Detener
sudo systemctl stop odoo

# Reiniciar
sudo systemctl restart odoo

# Ver estado
sudo systemctl status odoo

# Ver logs en tiempo real
sudo journalctl -u odoo -f
```

### Actualizar Código desde GitHub
```bash
# Conectar por SSH
ssh -i ssh-key.key ubuntu@TU_IP

# Detener Odoo
sudo systemctl stop odoo

# Actualizar código
cd /opt/odoo/custom/addons/peluqueria_canina_pro
sudo -u odoo git pull

# Actualizar módulo
sudo -u odoo /opt/odoo/odoo/odoo-bin -c /etc/odoo.conf -d peluqueria_db -u peluqueria_canina_pro --stop-after-init

# Reiniciar
sudo systemctl start odoo
```

### Backup Manual
```bash
# Backup de base de datos
sudo -u postgres pg_dump peluqueria_db > backup_$(date +%Y%m%d).sql

# Backup de archivos
sudo tar -czf filestore_$(date +%Y%m%d).tar.gz /var/lib/odoo/filestore
```

---

## 🔄 WORKFLOW DE DESARROLLO

### En tu PC Local
```bash
# Hacer cambios en el código
# ...

# Commit
git add .
git commit -m "Descripción del cambio"

# Push a GitHub
git push origin main
```

### En el Servidor
```bash
# Conectar
ssh -i ssh-key.key ubuntu@TU_IP

# Actualizar
cd /opt/odoo/custom/addons/peluqueria_canina_pro
sudo -u odoo git pull
sudo systemctl restart odoo
```

---

## 🆘 TROUBLESHOOTING

### Odoo no inicia
```bash
# Ver logs
sudo journalctl -u odoo -n 50 --no-pager

# Verificar PostgreSQL
sudo systemctl status postgresql

# Reiniciar todo
sudo systemctl restart postgresql
sudo systemctl restart odoo
```

### No puedo acceder desde el navegador
```bash
# Verificar firewall
sudo ufw status

# Verificar puerto
sudo netstat -tlnp | grep 8069

# Verificar Oracle Cloud Security List
# (debe tener regla para puerto 8069)
```

### Error de permisos
```bash
# Arreglar permisos
sudo chown -R odoo:odoo /opt/odoo /var/lib/odoo /var/log/odoo
```

---

## ✅ CHECKLIST FINAL

- [ ] Código subido a GitHub
- [ ] VM creada en Oracle Cloud
- [ ] Odoo instalado y funcionando
- [ ] Acceso desde navegador OK
- [ ] Módulos instalados
- [ ] Password de admin cambiado
- [ ] Backup configurado
- [ ] Comandos de control probados

---

**¡Listo! Tu sistema está en producción y puedes seguir desarrollando localmente.**
