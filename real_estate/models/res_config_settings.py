from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_number = fields.Char(
        string="Número WhatsApp",
        config_parameter='real_estate.whatsapp_number',
    )
    facebook_url = fields.Char(
        string="URL Facebook",
        config_parameter='real_estate.facebook_url',
    )
    instagram_url = fields.Char(
        string="URL Instagram",
        config_parameter='real_estate.instagram_url',
    )
    tiktok_url = fields.Char(
        string="URL TikTok",
        config_parameter='real_estate.tiktok_url',
    )
