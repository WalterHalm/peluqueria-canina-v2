from odoo import models, fields

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    def _post_process(self):
        result = super()._post_process()
        
        for tx in self:
            if tx.sale_order_ids and tx.state == 'done':
                for order in tx.sale_order_ids:
                    if order.website_id and not order.estado_rapido:
                        order.write({
                            'estado_rapido': 'nuevo',
                            'tiempo_inicio_estado': fields.Datetime.now(),
                            'tiempo_inicio_total': fields.Datetime.now(),
                            'sonido_activo': True,
                        })
                        order._detectar_tipo_entrega()
        
        return result
