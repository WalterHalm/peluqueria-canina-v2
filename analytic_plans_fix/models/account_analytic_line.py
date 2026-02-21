from odoo import models, fields

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    x_plan1_id = fields.Many2one('account.analytic.account', string='Plan 1')
    x_plan2_id = fields.Many2one('account.analytic.account', string='Plan 2')
    x_plan3_id = fields.Many2one('account.analytic.account', string='Plan 3')
