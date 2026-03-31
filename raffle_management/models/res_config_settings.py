from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Configuración del módulo de sorteos.
    Permite configurar las credenciales de WhatsApp API (Twilio/Meta)
    para envío de notificaciones y 2FA."""
    _inherit = 'res.config.settings'

    raffle_whatsapp_provider = fields.Selection(
        [('none', 'Deshabilitado'),
         ('twilio', 'Twilio'),
         ('meta', 'Meta Business API')],
        string='Proveedor WhatsApp',
        default='none',
        config_parameter='raffle_management.whatsapp_provider',
    )
    raffle_whatsapp_account_sid = fields.Char(
        string='Account SID / App ID',
        config_parameter='raffle_management.whatsapp_account_sid',
    )
    raffle_whatsapp_auth_token = fields.Char(
        string='Auth Token / Secret',
        config_parameter='raffle_management.whatsapp_auth_token',
    )
    raffle_whatsapp_from_number = fields.Char(
        string='Número de Envío (WhatsApp)',
        config_parameter='raffle_management.whatsapp_from_number',
        help='Número de WhatsApp desde el que se envían los mensajes. Ej: +14155238886',
    )
