/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Navbar } from "@point_of_sale/app/components/navbar/navbar";

patch(Navbar.prototype, {
    async sendToKitchen() {
        const currentOrder = this.pos.selectedOrder;
        if (!currentOrder || currentOrder.lines.length === 0) {
            alert("⚠️ No hay productos en la orden");
            return;
        }

        try {
            // Buscar mesa
            let tableName = null;
            const table = this.pos.selectedTable;
            
            if (table) {
                const floorName = table.floor_id ? (table.floor_id[1] || table.floor_id.name || '') : '';
                const tableNumber = table.table_number || table.name || table[1] || '';
                tableName = `${floorName}Mesa${tableNumber}`;
            }
            
            // Buscar nota general o recopilar notas de productos
            let generalNote = currentOrder.internal_note || '';
            
            if (!generalNote) {
                const productNotes = [];
                for (const line of currentOrder.lines) {
                    const rawNote = line.getNote() || '';
                    if (rawNote) {
                        try {
                            const noteArray = JSON.parse(rawNote);
                            if (Array.isArray(noteArray) && noteArray.length > 0) {
                                const noteText = noteArray.map(n => n.text || '').filter(t => t).join(' ');
                                if (noteText) {
                                    productNotes.push(`${line.getFullProductName()}: ${noteText}`);
                                }
                            }
                        } catch (e) {
                            if (rawNote !== '[]') {
                                productNotes.push(`${line.getFullProductName()}: ${rawNote}`);
                            }
                        }
                    }
                }
                if (productNotes.length > 0) {
                    generalNote = productNotes.join(' | ');
                }
            }
            
            // Obtener nombre del cliente
            let customerName = 'Cliente PoS';
            const partner = currentOrder.partner_id || currentOrder.partner;
            
            if (partner) {
                customerName = partner.name || partner[1] || 'Cliente PoS';
            }
            
            const orderData = {
                tracking_number: currentOrder.tracking_number,
                table_name: tableName,
                customer_name: customerName,
                general_note: generalNote,
                pos_reference: currentOrder.pos_reference || currentOrder.uid || currentOrder.tracking_number,
                products: currentOrder.lines
                    .filter(line => !line.combo_parent_id)
                    .map(line => {
                        let productNote = '';
                        const rawNote = line.getNote() || '';
                        
                        if (rawNote) {
                            try {
                                const noteArray = JSON.parse(rawNote);
                                if (Array.isArray(noteArray) && noteArray.length > 0) {
                                    productNote = noteArray.map(n => n.text || '').filter(t => t).join(' ');
                                }
                            } catch (e) {
                                productNote = rawNote;
                            }
                        }
                        
                        return {
                            name: line.getFullProductName(),
                            qty: line.qty,
                            note: productNote,
                            combo_items: currentOrder.lines
                                .filter(item => item.combo_parent_id && item.combo_parent_id.id === line.id)
                                .map(item => ({
                                    name: item.getFullProductName(),
                                    qty: item.qty
                                }))
                        };
                    })
            };

            const response = await fetch('/tu_pedido_v3/crear_pedido_simple', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: orderData
                })
            });

            const result = await response.json();
            
            if (result.result && result.result.success) {
                alert(`✅ ${result.result.message}`);
            } else {
                const errorMsg = result.result ? result.result.message : 'Error desconocido';
                alert(`❌ Error: ${errorMsg}`);
            }
        } catch (error) {
            alert(`❌ Error: ${error.message}`);
        }
    }
});