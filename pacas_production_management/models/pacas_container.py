from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PacasContainer(models.Model):
    _name = 'pacas.container'
    _description = 'Registro de Contenedor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'arrival_date desc, id desc'

    name = fields.Char(
        'Referencia', required=True, copy=False, readonly=True,
        default=lambda self: _('Nuevo'))
    container_number = fields.Char('Número de Contenedor', tracking=True)
    container_type = fields.Selection([
        ('20hc', '20 HC'),
        ('40hc', '40 HC'),
        ('40std', '40 STD'),
        ('other', 'Otro'),
    ], string='Tipo de Contenedor', default='40hc', tracking=True)
    supplier_id = fields.Many2one(
        'res.partner', 'Proveedor', required=True,
        tracking=True, check_company=True)
    purchase_order_id = fields.Many2one(
        'purchase.order', 'Orden de Compra',
        domain="[('partner_id', 'child_of', supplier_id), ('state', '=', 'purchase')]",
        tracking=True, check_company=True)
    lot_id = fields.Many2one(
        'stock.lot', 'Lote del Contenedor', tracking=True,
        check_company=True,
        help="Lote asignado a este contenedor para trazabilidad completa")
    arrival_date = fields.Datetime('Fecha de Llegada', tracking=True)

    # --- Pesos ---
    gross_weight = fields.Float('Peso Bruto (lb)', digits='Product Unit', tracking=True)
    net_weight = fields.Float('Peso Neto (lb)', digits='Product Unit', tracking=True)
    tare_weight = fields.Float('Peso Tara (lb)', digits='Product Unit')
    usable_weight = fields.Float(
        'Peso Utilizable (lb)', compute='_compute_usable_weight', store=True)
    classified_weight = fields.Float(
        'Peso Clasificado (lb)', compute='_compute_classified_weight', store=True)
    waste_weight = fields.Float(
        'Peso Desperdicio (lb)', compute='_compute_waste_weight', store=True)
    pending_weight = fields.Float(
        'Peso Pendiente (lb)', compute='_compute_pending_weight', store=True)

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('received', 'Recibido'),
        ('in_process', 'En Proceso'),
        ('classified', 'Clasificado'),
        ('closed', 'Cerrado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', tracking=True, copy=False)
    notes = fields.Html('Notas')
    company_id = fields.Many2one(
        'res.company', 'Compañía', required=True,
        default=lambda self: self.env.company)

    # --- Relaciones ---
    classification_batch_ids = fields.One2many(
        'pacas.classification.batch', 'container_id', 'Lotes de Clasificación')
    production_ids = fields.One2many(
        'mrp.production', 'pacas_container_id', 'Órdenes de Fabricación')
    picking_ids = fields.One2many(
        'stock.picking', 'pacas_container_id', 'Transferencias')

    # --- Contadores ---
    classification_count = fields.Integer(compute='_compute_counts')
    production_count = fields.Integer(compute='_compute_counts')
    picking_count = fields.Integer(compute='_compute_counts')

    # -------------------------------------------------------------------------
    # Cómputos
    # -------------------------------------------------------------------------
    @api.depends('net_weight', 'tare_weight')
    def _compute_usable_weight(self):
        for rec in self:
            rec.usable_weight = rec.net_weight - rec.tare_weight

    @api.depends('classification_batch_ids.state', 'classification_batch_ids.line_ids.weight')
    def _compute_classified_weight(self):
        for rec in self:
            rec.classified_weight = sum(
                rec.classification_batch_ids.filtered(
                    lambda b: b.state == 'done'
                ).mapped('line_ids.weight'))

    @api.depends('classification_batch_ids.state', 'classification_batch_ids.line_ids')    
    def _compute_waste_weight(self):
        for rec in self:
            rec.waste_weight = sum(
                rec.classification_batch_ids.filtered(
                    lambda b: b.state == 'done'
                ).mapped('line_ids').filtered(
                    lambda l: l.grade == 'waste'
                ).mapped('weight'))

    @api.depends('usable_weight', 'classified_weight')
    def _compute_pending_weight(self):
        for rec in self:
            rec.pending_weight = rec.usable_weight - rec.classified_weight

    def _compute_counts(self):
        for rec in self:
            rec.classification_count = len(rec.classification_batch_ids)
            rec.production_count = len(rec.production_ids)
            rec.picking_count = len(rec.picking_ids)

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'pacas.container') or _('Nuevo')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Acciones de workflow
    # -------------------------------------------------------------------------
    def action_receive(self):
        for rec in self:
            if not rec.arrival_date:
                rec.arrival_date = fields.Datetime.now()
            rec.state = 'received'

    def action_start_process(self):
        for rec in self:
            if rec.state != 'received':
                raise UserError(_("El contenedor debe estar recibido antes de procesar."))
            rec.state = 'in_process'

    def action_mark_classified(self):
        for rec in self:
            if rec.state != 'in_process':
                raise UserError(_("El contenedor debe estar en proceso."))
            rec.state = 'classified'

    def action_close(self):
        for rec in self:
            if rec.pending_weight > 0.5:
                raise UserError(_(
                    "No se puede cerrar: %.2f lb pendientes de clasificar. "
                    "Registre todo el peso o desperdicio antes de cerrar."
                ) % rec.pending_weight)
            open_batches = rec.classification_batch_ids.filtered(
                lambda b: b.state not in ('done', 'cancelled'))
            if open_batches:
                raise UserError(_(
                    "No se puede cerrar: hay %d lotes de clasificación abiertos."
                ) % len(open_batches))
            rec.state = 'closed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    # -------------------------------------------------------------------------
    # Smart buttons
    # -------------------------------------------------------------------------
    def action_view_classifications(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Clasificaciones'),
            'res_model': 'pacas.classification.batch',
            'view_mode': 'list,form',
            'domain': [('container_id', '=', self.id)],
            'context': {'default_container_id': self.id},
        }

    def action_view_productions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Órdenes de Fabricación'),
            'res_model': 'mrp.production',
            'view_mode': 'list,form',
            'domain': [('pacas_container_id', '=', self.id)],
        }

    def action_view_pickings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Transferencias'),
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('pacas_container_id', '=', self.id)],
        }

    def action_create_classification(self):
        self.ensure_one()
        if self.state not in ('in_process', 'received'):
            raise UserError(_("El contenedor debe estar recibido o en proceso."))
        if self.state == 'received':
            self.action_start_process()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva Clasificación'),
            'res_model': 'pacas.classification.batch',
            'view_mode': 'form',
            'context': {
                'default_container_id': self.id,
                'default_lot_source_id': self.lot_id.id,
            },
            'target': 'current',
        }
