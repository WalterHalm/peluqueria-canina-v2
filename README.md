# 🐕 Peluquería Canina v2 - Sistema Completo Odoo 19

Sistema profesional de gestión para peluquerías caninas con dos módulos integrados.

## 📦 Módulos Incluidos

### 1. peluqueria_canina (Base)
Módulo base con funcionalidades esenciales:
- Gestión de mascotas
- Gestión de clientes
- Turnos básicos

### 2. peluqueria_canina_pro (Profesional)
Módulo avanzado con:
- ✅ Sistema de turnos con calendario
- ✅ Historial de visitas completo
- ✅ Centro de costos con cálculo de ganancias
- ✅ Catálogo de servicios con productos
- ✅ Dashboard con KPIs en tiempo real
- ✅ Facturación automática
- ✅ Diseño responsive

## 🚀 Instalación Rápida

### Requisitos
- Odoo 19.0
- PostgreSQL 12+
- Python 3.10+

### Instalación Local
```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/peluqueria-canina-v2.git
cd peluqueria-canina-v2

# Copiar a addons de Odoo
cp -r peluqueria_canina /ruta/a/odoo/addons/
cp -r peluqueria_canina_pro /ruta/a/odoo/addons/

# Iniciar Odoo
./odoo-bin -c odoo.conf -d peluqueria_db -i peluqueria_canina,peluqueria_canina_pro
```

## 🌐 Deployment en Servidor

Ver documentación completa en: [peluqueria_canina_pro/GUIA_RAPIDA_DEPLOYMENT.md](peluqueria_canina_pro/GUIA_RAPIDA_DEPLOYMENT.md)

### Instalación Automática (Oracle Cloud)
```bash
# Conectar al servidor
ssh -i ssh-key.key ubuntu@TU_IP

# Clonar repositorio
cd /opt/odoo/custom/addons
git clone https://github.com/TU_USUARIO/peluqueria-canina-v2.git
cd peluqueria-canina-v2

# Ejecutar script de instalación
# Ver GUIA_RAPIDA_DEPLOYMENT.md para el script completo
```

## 📋 Comandos de Control

```bash
# Iniciar servicio
sudo systemctl start odoo

# Detener servicio
sudo systemctl stop odoo

# Reiniciar servicio
sudo systemctl restart odoo

# Ver estado
sudo systemctl status odoo

# Ver logs en vivo
sudo journalctl -u odoo -f
```

## 🔄 Actualizar desde GitHub

```bash
# En el servidor
cd /opt/odoo/custom/addons/peluqueria-canina-v2
sudo -u odoo git pull
sudo systemctl restart odoo
```

## 📚 Documentación

- [Guía de Deployment](peluqueria_canina_pro/GUIA_RAPIDA_DEPLOYMENT.md)
- [Resumen Ejecutivo](peluqueria_canina_pro/RESUMEN_EJECUTIVO.md)
- [Documentación Técnica](peluqueria_canina_pro/DESARROLLO.md)
- [Arquitectura](peluqueria_canina_pro/ARQUITECTURA_Y_DEPLOYMENT.md)

## 📄 Licencia

LGPL-3

## 🆘 Soporte

Issues: https://github.com/TU_USUARIO/peluqueria-canina-v2/issues

---

**Versión:** 19.0.2.1  
**Última actualización:** 2026-02-13
