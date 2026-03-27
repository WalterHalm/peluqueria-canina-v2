import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ICalExportController(http.Controller):

    @http.route('/ical/<int:product_id>/calendar.ics', type='http', auth='public')
    def export_ical(self, product_id, **kwargs):
        try:
            from icalendar import Calendar, Event
        except ImportError:
            return request.make_response('icalendar not installed', status=500)

        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists() or not product.rent_ok:
            return request.not_found()

        cal = Calendar()
        cal.add('prodid', '-//Real Estate Odoo//real_estate//ES')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', product.name)

        order_lines = request.env['sale.order.line'].sudo().search([
            ('product_id.product_tmpl_id', '=', product_id),
            ('is_rental', '=', True),
            ('order_id.state', 'in', ['sale', 'done']),
            ('order_id.rental_start_date', '!=', False),
        ])

        for line in order_lines:
            event = Event()
            event.add('summary', f'Reservado — {line.order_id.partner_id.name}')
            event.add('dtstart', line.order_id.rental_start_date.date())
            event.add('dtend', line.order_id.rental_return_date.date())
            event.add('uid', f'odoo-rental-{line.id}@real_estate')
            cal.add_component(event)

        return request.make_response(
            cal.to_ical(),
            headers=[
                ('Content-Type', 'text/calendar; charset=utf-8'),
                ('Content-Disposition', f'attachment; filename="{product.name}.ics"'),
            ],
        )
