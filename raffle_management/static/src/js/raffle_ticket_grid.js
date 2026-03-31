/** @odoo-module **/
/* Interactividad de la cuadrícula de tickets de rifa.
   Click en ticket → popup confirmación → agregar al carrito vía RPC. */

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RaffleTicketGrid = publicWidget.Widget.extend({
    selector: '.raffle-grid-container',
    events: {
        'click .raffle-ticket.raffle-available': '_onTicketClick',
    },

    start: function () {
        /* Inicializa el buscador de tickets */
        const section = this.el.closest('section');
        if (!section) return this._super.apply(this, arguments);

        const searchBtn = section.querySelector('.raffle-search-btn');
        const searchInput = section.querySelector('.raffle-search-input');
        if (searchBtn && searchInput) {
            searchBtn.addEventListener('click', () => this._onSearch(searchInput, section));
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this._onSearch(searchInput, section);
            });
        }
        return this._super.apply(this, arguments);
    },

    _onSearch: function (input, section) {
        /* Busca un número de ticket, valida que exista y muestra su estado.
           Si está disponible, ofrece agregarlo al carrito. */
        const resultDiv = section.querySelector('.raffle-search-result');
        const num = parseInt(input.value);
        const total = parseInt(this.el.dataset.total) || 0;

        // Validar rango
        if (!num || num < 1 || num > total) {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `<span class="text-danger">
                <i class="fa fa-exclamation-circle"></i>
                Ingresá un número entre 1 y ${total}
            </span>`;
            return;
        }

        // Buscar el ticket en la cuadrícula
        const ticketEl = this.el.querySelector(
            `.raffle-ticket[data-ticket-number="${num}"]`
        );
        if (!ticketEl) {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `<span class="text-danger">
                <i class="fa fa-exclamation-circle"></i>
                Ticket #${num} no encontrado
            </span>`;
            return;
        }

        const state = ticketEl.dataset.ticketState;
        const ticketId = ticketEl.dataset.ticketId;

        // Scroll al ticket y resaltarlo
        ticketEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        ticketEl.classList.add('raffle-highlight');
        setTimeout(() => ticketEl.classList.remove('raffle-highlight'), 2000);

        if (state === 'available') {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `
                <span class="text-success">
                    <i class="fa fa-check-circle"></i>
                    Ticket #${num} está <strong>disponible</strong>
                </span>
                <button class="btn btn-sm btn-primary ms-2 raffle-search-add"
                        data-ticket-id="${ticketId}" data-ticket-number="${num}">
                    <i class="fa fa-cart-plus"></i> Agregar al carrito
                </button>
            `;
            resultDiv.querySelector('.raffle-search-add').addEventListener('click', async (e) => {
                const btn = e.currentTarget;
                await this._addTicketToCart(ticketEl, btn.dataset.ticketId, btn.dataset.ticketNumber);
                resultDiv.innerHTML = `<span class="text-success">
                    <i class="fa fa-check"></i> Ticket #${num} agregado al carrito
                </span>`;
            });
        } else if (state === 'sold') {
            const buyer = ticketEl.dataset.buyer || 'Anónimo';
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `<span class="text-danger">
                <i class="fa fa-times-circle"></i>
                Ticket #${num} ya fue <strong>vendido</strong> a ${buyer}
            </span>`;
        } else if (state === 'winner') {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `<span class="text-warning">
                <i class="fa fa-trophy"></i>
                Ticket #${num} es el <strong>ganador</strong>
            </span>`;
        }
    },

    _onTicketClick: function (ev) {
        const ticketEl = ev.currentTarget;
        if (ticketEl.classList.contains('raffle-loading')) return;

        const ticketNumber = ticketEl.dataset.ticketNumber;
        const ticketId = ticketEl.dataset.ticketId;

        // Remover popup anterior si existe
        document.querySelectorAll('.raffle-popup').forEach(el => el.remove());

        // Crear mini popup de confirmación
        const popup = document.createElement('div');
        popup.className = 'raffle-popup';
        popup.innerHTML = `
            <div class="raffle-popup-content">
                <p><strong>Ticket #${ticketNumber}</strong></p>
                <p>¿Agregar al carrito?</p>
                <div class="d-flex gap-2 justify-content-center">
                    <button class="btn btn-sm btn-primary raffle-popup-confirm">
                        <i class="fa fa-cart-plus"></i> Agregar
                    </button>
                    <button class="btn btn-sm btn-secondary raffle-popup-cancel">
                        Cancelar
                    </button>
                </div>
            </div>
        `;

        // Posicionar popup cerca del ticket
        ticketEl.style.position = 'relative';
        ticketEl.appendChild(popup);

        // Botón confirmar
        popup.querySelector('.raffle-popup-confirm').addEventListener('click', async (e) => {
            e.stopPropagation();
            popup.remove();
            await this._addTicketToCart(ticketEl, ticketId, ticketNumber);
        });

        // Botón cancelar
        popup.querySelector('.raffle-popup-cancel').addEventListener('click', (e) => {
            e.stopPropagation();
            popup.remove();
        });

        // Cerrar al hacer clic fuera
        setTimeout(() => {
            document.addEventListener('click', function closePopup(e) {
                if (!popup.contains(e.target)) {
                    popup.remove();
                    document.removeEventListener('click', closePopup);
                }
            });
        }, 100);
    },

    _addTicketToCart: async function (ticketEl, ticketId, ticketNumber) {
        ticketEl.classList.add('raffle-loading');
        ticketEl.style.opacity = '0.5';

        try {
            const result = await rpc('/shop/raffle/add_ticket', {
                ticket_id: ticketId,
            });

            if (result.error) {
                alert(result.error);
                ticketEl.style.opacity = '1';
                ticketEl.classList.remove('raffle-loading');
                return;
            }

            // Marcar ticket como vendido visualmente
            ticketEl.classList.remove('raffle-available', 'raffle-loading');
            ticketEl.classList.add('raffle-sold');
            ticketEl.style.opacity = '1';
            ticketEl.dataset.ticketState = 'sold';

            // Actualizar carrito con patrón nativo de Odoo
            this._updateCartBadge(result.cart_quantity);

            // Actualizar contadores de la cuadrícula
            this._updateGridCounters();

        } catch (error) {
            console.error('Error al agregar ticket:', error);
            ticketEl.style.opacity = '1';
            ticketEl.classList.remove('raffle-loading');
            alert('Error al agregar el ticket. Intentá de nuevo.');
        }
    },

    _updateCartBadge: function (cartQuantity) {
        /* Actualiza el badge del carrito usando el mismo patrón que Odoo nativo */
        const badges = document.querySelectorAll('.my_cart_quantity');
        badges.forEach(badge => {
            badge.classList.remove('d-none');
            badge.textContent = cartQuantity || '';
            // Animación de zoom como hace Odoo
            badge.classList.add('o_mycart_zoom_animation');
            setTimeout(() => badge.classList.remove('o_mycart_zoom_animation'), 300);
        });
        // Mostrar el li padre del carrito si estaba oculto
        document.querySelectorAll('li.o_wsale_my_cart').forEach(li => {
            li.classList.remove('d-none');
        });
        sessionStorage.setItem('website_sale_cart_quantity', cartQuantity);
    },

    _updateGridCounters: function () {
        /* Actualiza los badges de disponibles/vendidos en la cuadrícula */
        const container = this.el;
        const available = container.querySelectorAll('.raffle-ticket.raffle-available').length;
        const sold = container.querySelectorAll('.raffle-ticket.raffle-sold').length;
        const total = container.querySelectorAll('.raffle-ticket').length;

        // Buscar los badges en la sección padre
        const section = container.closest('section');
        if (!section) return;

        const badges = section.querySelectorAll('.badge');
        badges.forEach(badge => {
            if (badge.textContent.includes('Disponibles')) {
                badge.innerHTML = `<i class="fa fa-check-circle"></i> Disponibles: ${available}`;
            } else if (badge.textContent.includes('Vendidos')) {
                badge.innerHTML = `<i class="fa fa-times-circle"></i> Vendidos: ${sold}`;
            }
        });

        // Actualizar barra de progreso
        const progressBar = section.querySelector('.progress-bar');
        if (progressBar && total > 0) {
            const pct = Math.round(sold / total * 100);
            progressBar.style.width = pct + '%';
            progressBar.textContent = pct + '% vendido';
        }
    },
});

export default publicWidget.registry.RaffleTicketGrid;
