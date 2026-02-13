# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class PeluqueriaDashboard(models.Model):
    _name = 'peluqueria.dashboard'
    _description = 'Dashboard Peluquería'

    name = fields.Char(default='Dashboard')
    
    # Filtros
    fecha_desde = fields.Date(string='Desde', default=fields.Date.today)
    fecha_hasta = fields.Date(string='Hasta', default=fields.Date.today)
    servicio_id = fields.Many2one('peluqueria.servicio', string='Servicio')
    periodo = fields.Selection([
        ('dia', 'Diario'),
        ('mes', 'Mensual'),
        ('trimestre', 'Trimestral'),
    ], string='Periodo', default='mes')
    
    # KPIs
    turnos_hoy = fields.Integer(compute='_compute_kpis')
    ventas_hoy = fields.Monetary(compute='_compute_kpis', currency_field='currency_id')
    turnos_pendientes = fields.Integer(compute='_compute_kpis')
    ganancia_hoy = fields.Monetary(compute='_compute_kpis', currency_field='currency_id')
    
    # Resumen periodo
    ventas_periodo = fields.Monetary(compute='_compute_resumen_periodo', currency_field='currency_id')
    costos_periodo = fields.Monetary(compute='_compute_resumen_periodo', currency_field='currency_id')
    ganancia_periodo = fields.Monetary(compute='_compute_resumen_periodo', currency_field='currency_id')
    margen_periodo = fields.Float(compute='_compute_resumen_periodo')
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    @api.depends('fecha_desde', 'fecha_hasta')
    def _compute_kpis(self):
        for record in self:
            hoy = fields.Date.today()
            
            # Turnos hoy
            record.turnos_hoy = self.env['peluqueria.turno'].search_count([
                ('fecha_hora', '>=', datetime.combine(hoy, datetime.min.time())),
                ('fecha_hora', '<=', datetime.combine(hoy, datetime.max.time())),
                ('state', '!=', 'cancelado')
            ])
            
            # Turnos pendientes
            record.turnos_pendientes = self.env['peluqueria.turno'].search_count([
                ('state', 'in', ['borrador', 'confirmado'])
            ])
            
            # Ventas y ganancia hoy
            visitas_hoy = self.env['peluqueria.visita'].search([
                ('fecha', '>=', datetime.combine(hoy, datetime.min.time())),
                ('fecha', '<=', datetime.combine(hoy, datetime.max.time())),
                ('state', '!=', 'cancelado')
            ])
            record.ventas_hoy = sum(visitas_hoy.mapped('total_venta'))
            record.ganancia_hoy = sum(visitas_hoy.mapped('ganancia'))

    @api.depends('fecha_desde', 'fecha_hasta', 'periodo', 'servicio_id')
    def _compute_resumen_periodo(self):
        for record in self:
            fecha_inicio = record.fecha_desde or fields.Date.today()
            fecha_fin = record.fecha_hasta or fields.Date.today()
            
            # Ajustar fechas según periodo
            if record.periodo == 'dia':
                fecha_inicio = fecha_fin = fields.Date.today()
            elif record.periodo == 'mes':
                fecha_inicio = fecha_fin.replace(day=1)
            elif record.periodo == 'trimestre':
                mes_inicio = ((fecha_fin.month - 1) // 3) * 3 + 1
                fecha_inicio = fecha_fin.replace(month=mes_inicio, day=1)
            
            domain = [
                ('fecha', '>=', datetime.combine(fecha_inicio, datetime.min.time())),
                ('fecha', '<=', datetime.combine(fecha_fin, datetime.max.time())),
                ('state', '!=', 'cancelado')
            ]
            
            if record.servicio_id:
                domain.append(('servicio_ids', 'in', record.servicio_id.id))
            
            visitas = self.env['peluqueria.visita'].search(domain)
            
            record.ventas_periodo = sum(visitas.mapped('total_venta'))
            record.costos_periodo = sum(visitas.mapped('costo_total'))
            record.ganancia_periodo = sum(visitas.mapped('ganancia'))
            record.margen_periodo = (record.ganancia_periodo / record.ventas_periodo * 100) if record.ventas_periodo else 0

    def action_ver_turnos_hoy(self):
        hoy = fields.Date.today()
        return {
            'name': 'Turnos de Hoy',
            'type': 'ir.actions.act_window',
            'res_model': 'peluqueria.turno',
            'view_mode': 'calendar,kanban,list,form',
            'domain': [
                ('fecha_hora', '>=', datetime.combine(hoy, datetime.min.time())),
                ('fecha_hora', '<=', datetime.combine(hoy, datetime.max.time())),
            ],
            'context': {'search_default_hoy': 1}
        }

    def action_ver_ventas_hoy(self):
        hoy = fields.Date.today()
        return {
            'name': 'Ventas de Hoy',
            'type': 'ir.actions.act_window',
            'res_model': 'peluqueria.visita',
            'view_mode': 'list,form',
            'domain': [
                ('fecha', '>=', datetime.combine(hoy, datetime.min.time())),
                ('fecha', '<=', datetime.combine(hoy, datetime.max.time())),
            ]
        }

    def action_ver_turnos_pendientes(self):
        return {
            'name': 'Turnos Pendientes',
            'type': 'ir.actions.act_window',
            'res_model': 'peluqueria.turno',
            'view_mode': 'kanban,list,form',
            'domain': [('state', 'in', ['borrador', 'confirmado'])]
        }
