from odoo import http
from odoo.http import request
import json
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class PosSimpleController(http.Controller):

    @http.route('/tu_pedido_v3/crear_pedido_simple', type='json', auth='user', csrf=False)
    def crear_pedido_simple(self, **kwargs):
        """Crear pedido simple en el dashboard desde datos del carrito PoS"""
        try:
            tracking_number = kwargs.get('tracking_number')
            table_name = kwargs.get('table_name', 'Mostrador')
            customer_name = kwargs.get('customer_name', 'Cliente PoS')
            products = kwargs.get('products', [])
            general_note = kwargs.get('general_note', '')
            pos_reference = kwargs.get('pos_reference', '')

            if not tracking_number or not products:
                return {'success': False, 'message': 'Datos incompletos'}
            
            # PUNTO 2: Verificar duplicados por pos_reference
            if pos_reference:
                existing = request.env['sale.order'].sudo().search([
                    ('pos_reference', '=', pos_reference),
                    ('estado_rapido', '!=', False)
                ], limit=1)
                if existing:
                    # Si existe, verificar si hay cambios
                    productos_originales = self._get_productos_snapshot(existing)
                    hay_cambios = self._hay_cambios_productos_boton(existing, products)
                    
                    if not hay_cambios:
                        # Sin cambios = error
                        return {'success': False, 'message': 'Error: Pedido ya enviado a cocina'}
                    else:
                        # Con cambios = actualizar y marcar modificado
                        productos_nuevos_snapshot = []
                        for p in products:
                            productos_nuevos_snapshot.append({
                                'name': p.get('name', ''),
                                'qty': p.get('qty', 1),
                                'full_name': p.get('name', '')
                            })
                        
                        detalles = self._calcular_detalles_cambios(productos_originales, productos_nuevos_snapshot)
                        
                        # Actualizar productos
                        existing.order_line.unlink()
                        self._crear_lineas_productos(existing, products)
                        
                        # Marcar como modificado si no está en estado nuevo
                        if existing.estado_rapido not in ['nuevo']:
                            existing.write({
                                'productos_modificados': True,
                                'detalles_cambios': str(detalles),
                                'nota_cocina': general_note.strip() if general_note and general_note.strip() else existing.nota_cocina
                            })
                        else:
                            existing.write({
                                'nota_cocina': general_note.strip() if general_note and general_note.strip() else existing.nota_cocina
                            })
                        
                        request.env.cr.commit()
                        return {'success': True, 'message': 'Productos modificados - enviado a cocina'}
            
            # Buscar o crear el partner
            partner = request.env['res.partner'].sudo().search([
                ('name', '=', customer_name)
            ], limit=1)
            
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'name': customer_name,
                    'is_company': False,
                })

            # Crear nombre correcto con mesa y número
            if table_name and table_name != 'Mostrador' and table_name != 'null' and table_name != 'None':
                order_name = f'{table_name}'
            else:
                order_name = f'Pedido-{tracking_number}'
            
            # Detectar si es delivery por productos
            is_delivery = any(
                'envio' in product_data.get('name', '').lower() or 
                'envío' in product_data.get('name', '').lower() or
                'delivery' in product_data.get('name', '').lower() or
                'entrega' in product_data.get('name', '').lower() or
                'estandar' in product_data.get('name', '').lower()
                for product_data in products
            )
            
            # PUNTO 1: Obtener dirección del partner si es delivery
            direccion_completa = False
            if is_delivery and partner:
                direccion_completa = self._format_address(partner)
            
            # Crear registro simple en sale.order para el dashboard
            order_vals = {
                'name': order_name,
                'partner_id': partner.id,
                'state': 'draft',
                'es_para_envio': is_delivery,
                'direccion_entrega_completa': direccion_completa,
                'estado_rapido': 'nuevo',
                'tiempo_inicio_estado': datetime.now(),
                'tiempo_inicio_total': datetime.now(),
                'sonido_activo': True,
                'nota_cocina': general_note.strip() if general_note and general_note.strip() else False,
                'pos_reference': pos_reference if pos_reference else False,
            }

            # Crear la orden
            order = request.env['sale.order'].sudo().create(order_vals)

            # Crear líneas de productos simples
            self._crear_lineas_productos(order, products)

            request.env.cr.commit()
            
            return {
                'success': True,
                'message': f'Pedido {order_name} creado y enviado a cocina',
                'order_id': order.id
            }

        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _crear_lineas_productos(self, order, products):
        """Crear líneas de productos para una orden"""
        for product_data in products:
            product = request.env['product.product'].sudo().search([
                ('name', '=', product_data.get('name', ''))
            ], limit=1)
            
            if not product:
                product = request.env['product.product'].sudo().create({
                    'name': product_data.get('name', 'Producto PoS'),
                    'type': 'consu',
                    'list_price': 0.0,
                })

            product_name = product_data.get('name', '')
            product_note = product_data.get('note', '')
            
            combo_items = product_data.get('combo_items', [])
            if combo_items:
                combo_names = [item.get('name', '') for item in combo_items]
                combo_text = f" ({', '.join(combo_names)})"
                final_product_name = f"{product_name}{combo_text}"
            else:
                final_product_name = product_name
            
            if product_note:
                final_product_name = f"{final_product_name} - {product_note}"
            
            line_vals = {
                'order_id': order.id,
                'product_id': product.id,
                'product_uom_qty': product_data.get('qty', 1),
                'price_unit': 0.0,
                'name': final_product_name,
            }
            request.env['sale.order.line'].sudo().create(line_vals)
    

    def _actualizar_orden_desde_boton(self, sale_order, products, general_note, table_name, tracking_number):
        """Actualizar orden existente desde el botón"""
        try:
            if not self._hay_cambios_productos_boton(sale_order, products):
                return False
            
            if sale_order.estado_rapido not in ['nuevo']:
                sale_order.write({'productos_modificados': True})
                request.env.cr.commit()
            
            sale_order.order_line.unlink()
            self._crear_lineas_productos(sale_order, products)
            
            sale_order.write({
                'nota_cocina': general_note.strip() if general_note and general_note.strip() else False,
                'tiempo_inicio_estado': request.env.cr.now(),
            })
            
            return True
        except Exception as e:
            return False
    
    def _hay_cambios_productos_boton(self, sale_order, products):
        """Verificar cambios desde el botón"""
        try:
            # Hash de productos del botón
            button_hash = []
            for product in products:
                name = product.get('name', '')
                note = product.get('note', '')
                full_name = f"{name} - {note}" if note else name
                item = f"{name}|{product.get('qty', 1)}|{full_name}"
                button_hash.append(item)
            button_hash.sort()
            
            # Hash de productos existentes
            sale_hash = []
            for line in sale_order.order_line:
                if not line.name.startswith('  →'):
                    item = f"{line.product_id.name}|{int(line.product_uom_qty)}|{line.name}"
                    sale_hash.append(item)
            sale_hash.sort()
            
            return button_hash != sale_hash
            
        except Exception as e:
            return True
    
    def _format_address(self, partner):
        """Formatear dirección completa del partner"""
        parts = []
        if partner.street:
            parts.append(partner.street)
        if partner.street2:
            parts.append(partner.street2)
        if partner.city:
            parts.append(partner.city)
        if partner.state_id:
            parts.append(partner.state_id.name)
        if partner.zip:
            parts.append(partner.zip)
        return ', '.join(parts) if parts else False
    
    def _get_productos_snapshot(self, sale_order):
        """Obtener snapshot de productos actuales"""
        productos = []
        for line in sale_order.order_line:
            productos.append({
                'name': line.product_id.name,
                'qty': line.product_uom_qty,
                'full_name': line.name
            })
        return productos
    
    def _calcular_detalles_cambios(self, productos_originales, productos_nuevos):
        """Calcular detalles de cambios entre productos"""
        detalles = {
            'agregados': [],
            'modificados': [],
            'eliminados': []
        }
        
        # Crear diccionarios por nombre
        orig_dict = {p['name']: p for p in productos_originales}
        new_dict = {p['name']: p for p in productos_nuevos}
        
        # Productos agregados
        for name, prod in new_dict.items():
            if name not in orig_dict:
                detalles['agregados'].append({'name': name, 'qty': prod['qty']})
            elif orig_dict[name]['qty'] != prod['qty']:
                detalles['modificados'].append({
                    'name': name,
                    'qty_original': orig_dict[name]['qty'],
                    'qty_nueva': prod['qty']
                })
        
        # Productos eliminados
        for name, prod in orig_dict.items():
            if name not in new_dict:
                detalles['eliminados'].append({'name': name, 'qty': prod['qty']})
        
        return detalles