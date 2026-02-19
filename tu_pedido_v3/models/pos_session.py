from odoo import models, fields, api

class PosSession(models.Model):
    _inherit = 'pos.session'
    
    fecha_apertura = fields.Datetime(string='Fecha de Apertura', default=fields.Datetime.now)
    hora_cierre_estimada = fields.Float(string='Hora de Cierre Estimada', default=22.0)
    
    @api.model
    def get_info_sesion_abierta(self):
        sesion = self.search([('state', '=', 'opened')], limit=1)
        if sesion:
            return {
                'abierto': True,
                'sesion_id': sesion.id,
                'nombre': sesion.name,
                'fecha_apertura': sesion.start_at.isoformat() if sesion.start_at else False,
                'usuario': sesion.user_id.name
            }
        return {'abierto': False}
