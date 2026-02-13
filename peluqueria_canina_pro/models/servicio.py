# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Servicio(models.Model):
    _name = 'peluqueria.servicio'
    _description = 'Servicios de Peluquería'
    _order = 'sequence, name'
    _rec_name = 'name'

    # Campos básicos
    name = fields.Char(
        string='Nombre del Servicio',
        required=True,
        translate=True,
        help="Ej: Baño Completo, Corte de Pelo, Deslanado"
    )
    
    code = fields.Char(
        string='Código',
        help="Código interno del servicio"
    )
    
    description = fields.Text(
        string='Descripción',
        translate=True,
        help="Descripción detallada del servicio"
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help="Desmarcar para ocultar el servicio sin eliminarlo"
    )
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help="Orden de visualización"
    )
    
    # Categorización
    categoria = fields.Selection([
        ('bano', 'Baño'),
        ('corte', 'Corte de Pelo'),
        ('estetica', 'Estética'),
        ('higiene', 'Higiene'),
        ('especial', 'Tratamiento Especial'),
        ('otro', 'Otro'),
    ], string='Categoría', default='bano', required=True)
    
    # Precios y costos
    precio = fields.Monetary(
        string='Precio de Venta',
        currency_field='currency_id',
        required=True,
        help="Precio que se cobra al cliente"
    )
    
    costo_estimado = fields.Monetary(
        string='Costo Estimado',
        currency_field='currency_id',
        compute='_compute_costo_estimado',
        store=True,
        help="Costo estimado de productos y materiales"
    )
    
    margen = fields.Float(
        string='Margen (%)',
        compute='_compute_margen',
        store=True,
        help="Margen de ganancia porcentual"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    # Duración
    duracion = fields.Float(
        string='Duración (horas)',
        default=1.0,
        help="Duración estimada del servicio en horas"
    )
    
    duracion_display = fields.Char(
        string='Duración',
        compute='_compute_duracion_display',
        help="Duración en formato legible"
    )
    
    # Productos relacionados
    producto_ids = fields.One2many(
        'peluqueria.servicio.producto',
        'servicio_id',
        string='Productos Utilizados'
    )
    
    # Estadísticas
    visita_count = fields.Integer(
        string='Veces Realizado',
        compute='_compute_visita_count',
        help="Cantidad de veces que se realizó este servicio"
    )
    
    # Color para vista kanban
    color = fields.Integer(string='Color', default=0)
    
    # Imagen
    image = fields.Image(
        string='Imagen',
        max_width=512,
        max_height=512,
        help="Imagen representativa del servicio"
    )
    
    @api.depends('precio', 'costo_estimado')
    def _compute_margen(self):
        for record in self:
            if record.precio and record.costo_estimado:
                record.margen = ((record.precio - record.costo_estimado) / record.precio) * 100
            else:
                record.margen = 0.0
    
    @api.depends('producto_ids.costo_total')
    def _compute_costo_estimado(self):
        for record in self:
            record.costo_estimado = sum(record.producto_ids.mapped('costo_total'))
    
    @api.depends('duracion')
    def _compute_duracion_display(self):
        for record in self:
            if record.duracion:
                horas = int(record.duracion)
                minutos = int((record.duracion - horas) * 60)
                if horas > 0 and minutos > 0:
                    record.duracion_display = f"{horas}h {minutos}min"
                elif horas > 0:
                    record.duracion_display = f"{horas}h"
                else:
                    record.duracion_display = f"{minutos}min"
            else:
                record.duracion_display = "No especificado"
    
    def _compute_visita_count(self):
        for record in self:
            record.visita_count = self.env['peluqueria.visita'].search_count([
                ('servicio_ids', 'in', record.id)
            ])
    
    @api.constrains('precio')
    def _check_precios(self):
        for record in self:
            if record.precio < 0:
                raise ValidationError("El precio no puede ser negativo")
    
    @api.constrains('duracion')
    def _check_duracion(self):
        for record in self:
            if record.duracion <= 0:
                raise ValidationError("La duración debe ser mayor a 0")
            if record.duracion > 24:
                raise ValidationError("La duración no puede ser mayor a 24 horas")
    
    def action_view_visitas(self):
        """Acción para ver las visitas que incluyen este servicio"""
        self.ensure_one()
        return {
            'name': f'Visitas con {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'peluqueria.visita',
            'view_mode': 'list,form',
            'domain': [('servicio_ids', 'in', self.id)],
            'context': {'default_servicio_ids': [(4, self.id)]},
        }


class ServicioProducto(models.Model):
    _name = 'peluqueria.servicio.producto'
    _description = 'Productos por Servicio'
    
    servicio_id = fields.Many2one('peluqueria.servicio', required=True, ondelete='cascade')
    producto_id = fields.Many2one('product.product', string='Producto', required=True)
    cantidad = fields.Float(string='Cantidad Usada', default=1.0, required=True, help="Cantidad que se usa del producto en este servicio")
    uom_id = fields.Many2one('uom.uom', string='Unidad', required=True)
    costo_unitario = fields.Float(string='Costo Unitario', related='producto_id.standard_price', readonly=True)
    costo_total = fields.Float(string='Costo Total', compute='_compute_costo_total', store=True)
    
    @api.onchange('producto_id')
    def _onchange_producto_id(self):
        if self.producto_id:
            self.uom_id = self.producto_id.uom_id
    
    @api.depends('cantidad', 'costo_unitario', 'uom_id', 'producto_id')
    def _compute_costo_total(self):
        for record in self:
            if record.producto_id and record.uom_id:
                if record.uom_id != record.producto_id.uom_id:
                    cantidad_base = record.uom_id._compute_quantity(
                        record.cantidad,
                        record.producto_id.uom_id,
                        rounding_method='HALF-UP'
                    )
                else:
                    cantidad_base = record.cantidad
                    
                record.costo_total = cantidad_base * record.costo_unitario
            else:
                record.costo_total = 0
