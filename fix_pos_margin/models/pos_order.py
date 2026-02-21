# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.tools import float_is_zero

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.depends('price_subtotal', 'product_id', 'qty')
    def _compute_margin(self):
        """Sobrescribir cálculo de margen con manejo de errores para pedidos migrados"""
        for line in self:
            try:
                # Verificar que currency_id existe y tiene rounding válido
                if not line.currency_id or not line.currency_id.rounding or line.currency_id.rounding <= 0:
                    line.margin = 0.0
                    line.margin_percent = 0.0
                    continue
                
                # Cálculo normal
                line.margin_percent = not float_is_zero(line.price_subtotal, precision_rounding=line.currency_id.rounding) \
                    and (line.price_subtotal - (line.product_id.standard_price * line.qty)) / line.price_subtotal or 0
                line.margin = line.price_subtotal - (line.product_id.standard_price * line.qty)
            except:
                # Si falla, establecer valores por defecto
                line.margin = 0.0
                line.margin_percent = 0.0
