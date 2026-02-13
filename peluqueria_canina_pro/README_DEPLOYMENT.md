# 🐕 Peluquería Canina PRO - Módulo Odoo 19

Sistema completo de gestión para peluquerías caninas con turnos, visitas, centro de costos y facturación.

## 🚀 Características

- ✅ **Gestión de Turnos** con calendario
- ✅ **Historial de Visitas** completo
- ✅ **Centro de Costos** con cálculo automático de ganancias
- ✅ **Catálogo de Servicios** con precios y productos
- ✅ **Dashboard** con KPIs en tiempo real
- ✅ **Facturación** automática
- ✅ **Diseño Responsive** (móvil, tablet, desktop)

## 📦 Instalación Local

### Requisitos
- Odoo 19.0
- PostgreSQL 12+
- Python 3.10+

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/TU_USUARIO/peluqueria_canina_pro.git
cd peluqueria_canina_pro
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

3. **Instalar módulo base (si no lo tienes)**
```bash
# Clonar módulo base
git clone https://github.com/TU_USUARIO/peluqueria_canina.git
```

4. **Iniciar Odoo**
```bash
./odoo-bin -c odoo.conf -d peluqueria_db -i peluqueria_canina,peluqueria_canina_pro
```

5. **Acceder**
- URL: http://localhost:8069
- Usuario: admin
- Password: admin (cambiar inmediatamente)

## 🌐 Deployment en Servidor

### Opción 1: Oracle Cloud (Gratis Permanente)

#### 1. Crear VM
```bash
# Conectar por SSH
ssh ubuntu@TU_IP_PUBLICA
```

#### 2. Instalar dependencias
```bash
sudo apt update
sudo apt install -y postgresql python3-pip python3-dev libxml2-dev libxslt1-dev \
    libldap2-dev libsasl2-dev libtiff5-dev libjpeg8-dev libopenjp2-7-dev \
    zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev \
    libfribidi-dev libxcb1-dev libpq-dev git
```

#### 3. Crear usuario Odoo
```bash
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo
```

#### 4. Instalar Odoo
```bash
sudo su - odoo
git clone https://github.com/odoo/odoo.git --depth 1 --branch 19.0 /opt/odoo/odoo
cd /opt/odoo/odoo
pip3 install -r requirements.txt
```

#### 5. Clonar módulos
```bash
mkdir -p /opt/odoo/custom/addons
cd /opt/odoo/custom/addons
git clone https://github.com/TU_USUARIO/peluqueria_canina.git
git clone https://github.com/TU_USUARIO/peluqueria_canina_pro.git
```

#### 6. Configurar PostgreSQL
```bash
sudo su - postgres
createuser -s odoo
createdb -O odoo peluqueria_db
exit
```

#### 7. Configurar Odoo
```bash
sudo cp /opt/odoo/custom/addons/peluqueria_canina_pro/odoo.conf.example /etc/odoo.conf
sudo nano /etc/odoo.conf
# Editar credenciales y rutas
```

#### 8. Crear servicio systemd
```bash
sudo nano /etc/systemd/system/odoo.service
```

Contenido:
```ini
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
```

#### 9. Iniciar servicio
```bash
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo
```

#### 10. Verificar
```bash
sudo systemctl status odoo
```

### Comandos de Control

```bash
# Iniciar Odoo
sudo systemctl start odoo

# Detener Odoo
sudo systemctl stop odoo

# Reiniciar Odoo
sudo systemctl restart odoo

# Ver estado
sudo systemctl status odoo

# Ver logs en tiempo real
sudo journalctl -u odoo -f

# Ver logs completos
sudo tail -f /var/log/odoo/odoo.log
```

### Actualizar Módulo

```bash
# Detener servicio
sudo systemctl stop odoo

# Actualizar código
cd /opt/odoo/custom/addons/peluqueria_canina_pro
sudo -u odoo git pull

# Actualizar módulo en Odoo
sudo -u odoo /opt/odoo/odoo/odoo-bin -c /etc/odoo.conf -d peluqueria_db -u peluqueria_canina_pro

# Reiniciar servicio
sudo systemctl start odoo
```

## 🔒 Seguridad

### Firewall
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Nginx (Proxy Reverso)
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/odoo
```

Contenido:
```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

server {
    listen 80;
    server_name tu-dominio.com;

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    location / {
        proxy_pass http://odoo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL con Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

## 📊 Backup

### Backup Manual
```bash
# Backup de base de datos
sudo -u postgres pg_dump peluqueria_db > backup_$(date +%Y%m%d).sql

# Backup de filestore
sudo tar -czf filestore_$(date +%Y%m%d).tar.gz /var/lib/odoo/filestore
```

### Backup Automático (Cron)
```bash
sudo crontab -e
```

Agregar:
```cron
# Backup diario a las 2 AM
0 2 * * * /opt/odoo/scripts/backup.sh
```

## 📝 Desarrollo

### Workflow de Git
```bash
# Crear rama para nueva feature
git checkout -b feature/nueva-funcionalidad

# Hacer cambios y commit
git add .
git commit -m "Descripción del cambio"

# Push a GitHub
git push origin feature/nueva-funcionalidad

# Crear Pull Request en GitHub
# Después de merge, actualizar servidor
```

### Actualizar en Servidor
```bash
ssh ubuntu@TU_IP
cd /opt/odoo/custom/addons/peluqueria_canina_pro
sudo -u odoo git pull
sudo systemctl restart odoo
```

## 🐛 Troubleshooting

### Ver logs
```bash
sudo journalctl -u odoo -n 100 --no-pager
```

### Reiniciar PostgreSQL
```bash
sudo systemctl restart postgresql
```

### Limpiar sesiones
```bash
sudo rm -rf /var/lib/odoo/sessions/*
```

## 📚 Documentación

- [Manual de Usuario](./MANUAL_USUARIO.md)
- [Documentación Técnica](./DESARROLLO.md)
- [Arquitectura y Deployment](./ARQUITECTURA_Y_DEPLOYMENT.md)

## 📄 Licencia

LGPL-3

## 👥 Autor

Tu Nombre - [GitHub](https://github.com/TU_USUARIO)

## 🆘 Soporte

- Issues: https://github.com/TU_USUARIO/peluqueria_canina_pro/issues
- Email: tu@email.com
