import logging
import requests
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from icalendar import Calendar
    ICALENDAR_AVAILABLE = True
except ImportError:
    ICALENDAR_AVAILABLE = False
    _logger.warning("icalendar no instalado. Instalar con: pip install icalendar")


class ICalSync(models.Model):
    _name = 'real.estate.ical.sync'
    _description = 'Sincronización iCal de Propiedad'

    product_id = fields.Many2one(
        'product.template', string="Propiedad",
        required=True, ondelete='cascade',
        domain=[('rent_ok', '=', True)],
    )
    platform = fields.Selection([
        ('airbnb', 'Airbnb'),
        ('booking', 'Booking.com'),
        ('other', 'Otro'),
    ], string="Plataforma", required=True)
    ical_url = fields.Char(string="URL del Calendario (.ics)", required=True)
    last_sync = fields.Datetime(string="Última Sincronización", readonly=True)
    sync_status = fields.Char(string="Estado", readonly=True)
    blocked_line_ids = fields.One2many(
        'real.estate.blocked.period', 'sync_id', string="Períodos Bloqueados"
    )

    def action_sync_now(self):
        for sync in self:
            sync._do_sync()

    def _do_sync(self):
        self.ensure_one()
        if not ICALENDAR_AVAILABLE:
            raise UserError("Instalar la librería icalendar: pip install icalendar")
        try:
            response = requests.get(self.ical_url, timeout=15)
            response.raise_for_status()
            cal = Calendar.from_ical(response.content)

            self.blocked_line_ids.unlink()

            new_periods = []
            for component in cal.walk():
                if component.name != 'VEVENT':
                    continue
                dtstart = component.get('DTSTART')
                dtend = component.get('DTEND')
                if not dtstart or not dtend:
                    continue
                start = dtstart.dt
                end = dtend.dt
                if isinstance(start, datetime):
                    start = start.date()
                if isinstance(end, datetime):
                    end = end.date()
                new_periods.append({
                    'sync_id': self.id,
                    'product_id': self.product_id.id,
                    'date_start': start,
                    'date_end': end,
                    'summary': str(component.get('SUMMARY', 'Reserva externa')),
                })

            self.env['real.estate.blocked.period'].create(new_periods)
            self.write({
                'last_sync': fields.Datetime.now(),
                'sync_status': f'OK — {len(new_periods)} períodos importados',
            })
        except Exception as e:
            self.write({'sync_status': f'Error: {str(e)}'})
            _logger.exception("Error sincronizando iCal para %s: %s", self.product_id.name, e)

    @api.model
    def _cron_sync_all(self):
        self.search([])._do_sync()


class BlockedPeriod(models.Model):
    _name = 'real.estate.blocked.period'
    _description = 'Período Bloqueado por Reserva Externa'

    sync_id = fields.Many2one('real.estate.ical.sync', ondelete='cascade')
    product_id = fields.Many2one('product.template', string="Propiedad", required=True)
    date_start = fields.Date(string="Desde", required=True)
    date_end = fields.Date(string="Hasta", required=True)
    summary = fields.Char(string="Descripción")
