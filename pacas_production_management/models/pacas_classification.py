from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PacasClassificationBatch(models.Model):
    _name = 'pacas.classification.batch'
    _description = 'Lote de Clasificación'
    _inherit = ['mail.thread']
    _order = 'date_start desc, id desc'

    name = fields.Char(
        'Referencia', required=True, copy=False, readonly=True,
        default=lambda self: _('Nuevo'))
    container_id = fields.Many2one(
        'pacas.container', 'Contenedor', required=True,
        ondelete='cascade', tracking=True)
    lot_source_id = fields.Many2one(
        'stock.lot', 'Lote Origen',
        related='container_id.lot_id', store=True, readonly=True)
    date_start = fields.Datetime('Fecha Inicio', tracking=True)
    date_end = fields.Datetime('Fecha Fin', tracking=True)
    operator_ids = fields.Many2many(
        'res.users', 'pacas_classification_operator_rel',
        'batch_id', 'user_id', string='Operadores')
    line_ids = fields.One2many(
        'pacas.classification.line', 'batch_id', 'Líneas de Clasificación')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('done', 'Hecho'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', tracking=True, copy=False)
    company_id = fields.Many2one(
        related='container_id.company_id', store=True)

    total_weight = fields.Float(
        'Peso Total (lb)', compute='_compute_total_weight', store=True)
    available_weight = fields.Float(
        'Peso Disponible (lb)', compute='_compute_available_weight')

    # MOs generadas al validar
    production_ids = fields.One2many(
        'mrp.production', 'pacas_classification_batch_id',
        'Órdenes de Fabricación Generadas', readonly=True)
    production_count = fields.Integer(compute='_compute_production_count')

    @api.depends('line_ids.weight')
    def _compute_total_weight(self):
        for rec in self:
            rec.total_weight = sum(rec.line_ids.mapped('weight'))

    @api.depends('container_id.usable_weight', 'container_id.classified_weight')
    def _compute_available_weight(self):
        for rec in self:
            container = rec.container_id
            already = container.classified_weight
            if rec.state != 'done':
                already -= rec.total_weight
            rec.available_weight = container.usable_weight - already

    def _compute_production_count(self):
        for rec in self:
            rec.production_count = len(rec.production_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'pacas.classification.batch') or _('Nuevo')
        return super().create(vals_list)

    @api.constrains('line_ids')
    def _check_weight_limit(self):
        for rec in self:
            container = rec.container_id
            other_batches_weight = sum(
                container.classification_batch_ids.filtered(
                    lambda b: b.id != rec.id and b.state == 'done'
                ).mapped('total_weight'))
            if (other_batches_weight + rec.total_weight) > container.usable_weight + 0.5:
                raise ValidationError(_(
                    "El peso clasificado total (%.2f lb) excede el "
                    "peso utilizable del contenedor (%.2f lb)."
                ) % (other_batches_weight + rec.total_weight, container.usable_weight))

    # -------------------------------------------------------------------------
    # Acciones de workflow
    # -------------------------------------------------------------------------
    def action_start(self):
        for rec in self:
            if not rec.date_start:
                rec.date_start = fields.Datetime.now()
            rec.state = 'in_progress'

    def action_validate(self):
        """Validar clasificación y generar MOs nativas para cada línea con producto+BoM."""
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Agregue al menos una línea de clasificación."))
            if not rec.date_end:
                rec.date_end = fields.Datetime.now()
            rec._generate_lots()
            rec._generate_production_orders()
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    # -------------------------------------------------------------------------
    # Generación de lotes
    # -------------------------------------------------------------------------
    def _generate_lots(self):
        """Crear lotes de resultado para líneas que tengan producto con tracking por lote."""
        for rec in self:
            for line in rec.line_ids:
                if not line.product_id or line.lot_result_id:
                    continue
                if line.product_id.tracking == 'lot':
                    line.lot_result_id = self.env['stock.lot'].create({
                        'name': '%s-%s' % (rec.name, line.product_id.default_code or line.id),
                        'product_id': line.product_id.id,
                        'company_id': rec.company_id.id,
                    })

    # -------------------------------------------------------------------------
    # Generación de MOs nativas
    # -------------------------------------------------------------------------
    def _generate_production_orders(self):
        """Para cada línea con producto que tenga BoM, crear una MO nativa.
        
        Esto conecta la clasificación rápida con el flujo de manufactura
        estándar de Odoo (BoM, work orders, lotes, etc.)
        """
        MrpProduction = self.env['mrp.production']
        for rec in self:
            for line in rec.line_ids.filtered(lambda l: l.product_id):
                bom = self.env['mrp.bom']._bom_find(
                    line.product_id,
                    company_id=rec.company_id.id,
                )
                if not bom:
                    continue
                # Obtener la BoM correcta para este producto
                product_bom = bom.get(line.product_id, self.env['mrp.bom'])
                if not product_bom:
                    continue
                mo = MrpProduction.create({
                    'product_id': line.product_id.id,
                    'product_qty': line.weight,
                    'product_uom_id': line.product_id.uom_id.id,
                    'bom_id': product_bom.id,
                    'origin': '%s / %s' % (rec.container_id.name, rec.name),
                    'pacas_container_id': rec.container_id.id,
                    'pacas_classification_batch_id': rec.id,
                })
                line.production_id = mo

    # -------------------------------------------------------------------------
    # Smart buttons
    # -------------------------------------------------------------------------
    def action_view_productions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Órdenes de Fabricación'),
            'res_model': 'mrp.production',
            'view_mode': 'list,form',
            'domain': [('pacas_classification_batch_id', '=', self.id)],
        }


class PacasClassificationLine(models.Model):
    _name = 'pacas.classification.line'
    _description = 'Línea de Clasificación'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    batch_id = fields.Many2one(
        'pacas.classification.batch', 'Lote',
        required=True, ondelete='cascade')
    container_id = fields.Many2one(
        related='batch_id.container_id', store=True)
    category_type = fields.Selection([
        ('men', 'Hombre'),
        ('women', 'Mujer'),
        ('children', 'Niños'),
        ('shoes', 'Zapatos'),
        ('bags', 'Bolsos/Carteras'),
        ('accessories', 'Accesorios'),
        ('other', 'Otro'),
    ], string='Categoría', required=True)
    grade = fields.Selection([
        ('premium', 'Premium'),
        ('a', 'Grado A'),
        ('b', 'Grado B'),
        ('c', 'Grado C'),
        ('waste', 'Desperdicio'),
    ], string='Calidad', required=True)
    product_id = fields.Many2one(
        'product.product', 'Producto Resultante',
        domain="[('type', '=', 'consu')]",
        help="Producto intermedio o terminado (paca) que se fabricará")
    weight = fields.Float('Peso (lb)', digits='Product Unit', required=True)
    lot_source_id = fields.Many2one(
        'stock.lot', 'Lote Origen',
        related='batch_id.lot_source_id', store=True)
    lot_result_id = fields.Many2one(
        'stock.lot', 'Lote Resultado',
        help="Lote asignado a la producción resultante")
    production_id = fields.Many2one(
        'mrp.production', 'Orden de Fabricación', readonly=True,
        help="OF generada automáticamente al validar la clasificación")
    remarks = fields.Char('Observaciones')
