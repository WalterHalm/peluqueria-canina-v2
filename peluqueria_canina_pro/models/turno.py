# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Turno(models.Model):
    _name = 'peluqueria.turno'
    _description = 'Turnos de Peluquería'
    _order = 'fecha_hora desc'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Información básica
    display_name = fields.Char(
        string='Turno',
        compute='_compute_display_name',
        store=True
    )
    
    mascota_id = fields.Many2one(
        'peluqueria.mascota',
        string='Mascota',
        required=True,
        tracking=True,
        ondelete='restrict'
    )
    
    cliente_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='mascota_id.owner_id',
        store=True,
        readonly=True
    )
    
    telefono = fields.Char(
        string='Teléfono',
        related='cliente_id.phone',
        readonly=True
    )
    
    # Fecha y hora
    fecha_hora = fields.Datetime(
        string='Fecha y Hora',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        help="Fecha y hora del turno"
    )
    
    fecha_hora_fin = fields.Datetime(
        string='Hora Fin',
        compute='_compute_fecha_hora_fin',
        store=True,
        help="Hora estimada de finalización"
    )
    
    duracion_total = fields.Float(
        string='Duración Total (horas)',
        compute='_compute_duracion_total',
        store=True,
        help="Duración total estimada según servicios"
    )
    
    # Servicios
    servicio_ids = fields.Many2many(
        'peluqueria.servicio',
        string='Servicios',
        required=True,
        help="Servicios a realizar en este turno"
    )
    
    # Estado del turno
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('asistio', 'Asistió'),
        ('no_asistio', 'No Asistió'),
    ], string='Estado', default='borrador', required=True, tracking=True, copy=False)
    
    # Notas
    notas = fields.Text(
        string='Notas',
        help="Observaciones o instrucciones especiales"
    )
    
    motivo_cancelacion = fields.Text(
        string='Motivo de Cancelación',
        tracking=True
    )
    
    # Empleado asignado
    empleado_id = fields.Many2one(
        'res.users',
        string='Peluquero Asignado',
        tracking=True,
        help="Empleado que atenderá este turno"
    )
    
    # Recordatorios
    recordatorio_enviado = fields.Boolean(
        string='Recordatorio Enviado',
        default=False,
        help="Indica si se envió recordatorio al cliente"
    )
    
    fecha_recordatorio = fields.Datetime(
        string='Fecha Recordatorio',
        readonly=True
    )
    
    # Relación con visita
    visita_id = fields.Many2one(
        'peluqueria.visita',
        string='Visita Generada',
        readonly=True,
        help="Visita creada al completar el turno"
    )
    
    # Campos computados para vista
    color = fields.Integer(
        string='Color',
        compute='_compute_color'
    )
    
    es_hoy = fields.Boolean(
        string='Es Hoy',
        compute='_compute_es_hoy'
    )
    
    esta_atrasado = fields.Boolean(
        string='Atrasado',
        compute='_compute_esta_atrasado'
    )
    
    @api.depends('mascota_id', 'fecha_hora')
    def _compute_display_name(self):
        for record in self:
            if record.mascota_id and record.fecha_hora:
                fecha_str = fields.Datetime.context_timestamp(
                    record, record.fecha_hora
                ).strftime('%d/%m/%Y %H:%M')
                record.display_name = f"{record.mascota_id.name} - {fecha_str}"
            else:
                record.display_name = "Nuevo Turno"
    
    @api.depends('servicio_ids')
    def _compute_duracion_total(self):
        for record in self:
            record.duracion_total = sum(record.servicio_ids.mapped('duracion'))
    
    @api.depends('fecha_hora', 'duracion_total')
    def _compute_fecha_hora_fin(self):
        for record in self:
            if record.fecha_hora and record.duracion_total:
                record.fecha_hora_fin = record.fecha_hora + timedelta(hours=record.duracion_total)
            else:
                record.fecha_hora_fin = record.fecha_hora
    
    @api.depends('state')
    def _compute_color(self):
        color_map = {
            'borrador': 7,      # Gris
            'confirmado': 4,    # Azul
            'asistio': 10,      # Verde
            'no_asistio': 1,    # Rojo
        }
        for record in self:
            record.color = color_map.get(record.state, 0)
    
    @api.depends('fecha_hora')
    def _compute_es_hoy(self):
        hoy = fields.Date.today()
        for record in self:
            if record.fecha_hora:
                fecha_turno = record.fecha_hora.date()
                record.es_hoy = fecha_turno == hoy
            else:
                record.es_hoy = False
    
    @api.depends('fecha_hora', 'state')
    def _compute_esta_atrasado(self):
        ahora = fields.Datetime.now()
        for record in self:
            record.esta_atrasado = (
                record.fecha_hora < ahora and 
                record.state in ['borrador', 'confirmado']
            )
    
    @api.constrains('fecha_hora')
    def _check_fecha_hora(self):
        for record in self:
            if record.fecha_hora < fields.Datetime.now() and record.state == 'borrador':
                raise ValidationError("No se puede crear un turno en el pasado")
    
    def action_confirmar(self):
        """Confirmar el turno"""
        self.write({'state': 'confirmado'})
        return True
    
    def action_no_asistio(self):
        """Marcar como no asistió"""
        self.write({'state': 'no_asistio'})
        return True
    
    def action_completar(self):
        """Completar turno y crear visita"""
        self.ensure_one()
        
        # Preparar líneas de productos desde servicios
        producto_lines = []
        for servicio in self.servicio_ids:
            for prod_line in servicio.producto_ids:
                producto_lines.append((0, 0, {
                    'producto_id': prod_line.producto_id.id,
                    'cantidad': prod_line.cantidad,
                    'uom_id': prod_line.uom_id.id,
                }))
        
        # Crear visita automáticamente
        visita = self.env['peluqueria.visita'].create({
            'mascota_id': self.mascota_id.id,
            'fecha': self.fecha_hora,
            'turno_id': self.id,
            'servicio_ids': [(6, 0, self.servicio_ids.ids)],
            'empleado_id': self.empleado_id.id if self.empleado_id else False,
            'notas': self.notas,
            'producto_line_ids': producto_lines,
        })
        
        self.write({
            'state': 'asistio',
            'visita_id': visita.id,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'peluqueria.visita',
            'res_id': visita.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_enviar_recordatorio(self):
        """Enviar recordatorio al cliente"""
        # TODO: Implementar envío de email/SMS
        self.write({
            'recordatorio_enviado': True,
            'fecha_recordatorio': fields.Datetime.now(),
        })
        return True
