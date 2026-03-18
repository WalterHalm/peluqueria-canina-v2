from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    pacas_container_id = fields.Many2one(
        'pacas.container', 'Contenedor Origen',
        index='btree_not_null', check_company=True,
        help="Contenedor del cual se origina esta producción")
    pacas_classification_batch_id = fields.Many2one(
        'pacas.classification.batch', 'Lote de Clasificación',
        index='btree_not_null',
        help="Clasificación que generó esta orden de fabricación")
