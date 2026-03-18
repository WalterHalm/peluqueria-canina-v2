from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    pacas_container_ids = fields.One2many(
        'pacas.container', 'purchase_order_id', string='Contenedores')
    pacas_container_count = fields.Integer(
        compute='_compute_pacas_container_count')

    def _compute_pacas_container_count(self):
        for rec in self:
            rec.pacas_container_count = len(rec.pacas_container_ids)

    def action_view_pacas_containers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contenedores',
            'res_model': 'pacas.container',
            'view_mode': 'list,form',
            'domain': [('purchase_order_id', '=', self.id)],
            'context': {
                'default_purchase_order_id': self.id,
                'default_supplier_id': self.partner_id.id,
            },
        }
