# INSTRUCCIONES PARA CREAR EL ICONO

El archivo icon.svg contiene el diseño del icono.

Para convertirlo a PNG (128x128):

## Opción 1: Online
1. Ve a https://cloudconvert.com/svg-to-png
2. Sube icon.svg
3. Configura tamaño: 128x128
4. Descarga como icon.png

## Opción 2: Con Inkscape
1. Abre icon.svg en Inkscape
2. File > Export PNG Image
3. Tamaño: 128x128
4. Guarda como icon.png

## Opción 3: Con ImageMagick
```bash
convert icon.svg -resize 128x128 icon.png
```

Coloca el archivo icon.png en:
c:\Program Files\Odoo 19.0.20251002\server\odoo\addons_extras\ecommerce_aberturas\static\description\icon.png
