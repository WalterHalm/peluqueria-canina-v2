# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Mascota(models.Model):
    _inherit = 'peluqueria.mascota'

    # Relaciones con módulo PRO
    turno_ids = fields.One2many(
        'peluqueria.turno',
        'mascota_id',
        string='Turnos'
    )
    
    visita_ids = fields.One2many(
        'peluqueria.visita',
        'mascota_id',
        string='Historial de Visitas'
    )
    
    # Estadísticas
    turno_count = fields.Integer(
        string='Total Turnos',
        compute='_compute_counts'
    )
    
    visita_count = fields.Integer(
        string='Total Visitas',
        compute='_compute_counts'
    )
    
    ultima_visita = fields.Date(
        string='Última Visita',
        compute='_compute_ultima_visita',
        store=True
    )
    
    proxima_visita = fields.Datetime(
        string='Próxima Visita',
        compute='_compute_proxima_visita',
        store=True
    )
    
    total_gastado = fields.Monetary(
        string='Total Gastado',
        compute='_compute_total_gastado',
        currency_field='currency_id',
        help="Total gastado por el cliente en esta mascota"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    @api.depends('turno_ids', 'visita_ids')
    def _compute_counts(self):
        for record in self:
            record.turno_count = len(record.turno_ids)
            record.visita_count = len(record.visita_ids)
    
    @api.depends('visita_ids.fecha')
    def _compute_ultima_visita(self):
        for record in self:
            if record.visita_ids:
                ultima = max(record.visita_ids.mapped('fecha'))
                record.ultima_visita = ultima.date() if ultima else False
            else:
                record.ultima_visita = False
    
    @api.depends('turno_ids.fecha_hora', 'turno_ids.state')
    def _compute_proxima_visita(self):
        for record in self:
            turnos_futuros = record.turno_ids.filtered(
                lambda t: t.fecha_hora >= fields.Datetime.now() and t.state in ['confirmado', 'borrador']
            )
            if turnos_futuros:
                record.proxima_visita = min(turnos_futuros.mapped('fecha_hora'))
            else:
                record.proxima_visita = False
    
    @api.depends('visita_ids.total_venta')
    def _compute_total_gastado(self):
        for record in self:
            visitas_validas = record.visita_ids.filtered(lambda v: v.state != 'cancelado')
            record.total_gastado = sum(v.total_venta or 0 for v in visitas_validas)
    
    def action_ver_turnos(self):
        """Ver turnos de esta mascota"""
        self.ensure_one()
        return {
            'name': f'Turnos de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'peluqueria.turno',
            'view_mode': 'list,calendar,form',
            'domain': [('mascota_id', '=', self.id)],
            'context': {'default_mascota_id': self.id},
        }
    
    def action_ver_visitas(self):
        """Ver historial de visitas"""
        self.ensure_one()
        return {
            'name': f'Historial de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'peluqueria.visita',
            'view_mode': 'list,form',
            'domain': [('mascota_id', '=', self.id)],
            'context': {'default_mascota_id': self.id},
        }
    
    def action_agendar_turno(self):
        """Agendar nuevo turno"""
        self.ensure_one()
        return {
            'name': f'Nuevo Turno para {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'peluqueria.turno',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_mascota_id': self.id},
        }
