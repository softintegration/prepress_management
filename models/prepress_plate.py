# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from random import randint
from odoo.tools.float_utils import float_compare

DEFAULT_CODE_PLATE = "prepress.plate"


class PrepressPlate(models.Model):
    _name = 'prepress.plate'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'cancel.motif.class']
    _description = "Plate"

    name = fields.Char(string='Name', required=True, copy=False, index=True,
                       states={'draft': [('readonly', False)]}, readonly=True, default='New')
    state = fields.Selection([('draft', 'Draft'),
                              ('validated', 'Validated'),
                              ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False,
                             tracking=True, default='draft')
    product_plate_type = fields.Selection([('plate_ctp', 'CTP Plate'),
                                           ('plate_varnish', 'Varnish Plate')], string='Type',
                                          states={'draft': [('readonly', False)]}, readonly=True)
    product_varnish_id = fields.Many2one('product.product', string='Varnish', states={'draft': [('readonly', False)]},
                                         readonly=True)
    date = fields.Date(string='Date',states={'draft': [('readonly', False)]}, readonly=True)
    cutting_die_id = fields.Many2one('prepress.cutting.die', string="Cutting Die",
                                     states={'draft': [('readonly', False)]},
                                     readonly=True)
    exposure_nbr = fields.Integer('Exposure Nbr', states={'draft': [('readonly', False)]}, readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 states={'draft': [('readonly', False)]}, readonly=True,
                                 domain=[('customer_rank', '>', 0), ('parent_id', '=', False)])
    product_id = fields.Many2one('product.product', string='Product', states={'draft': [('readonly', False)]},
                                 readonly=True, domain=[('type', '=', 'product')])
    product_height = fields.Float(related='product_id.height')
    product_height_uom_id = fields.Many2one(related='product_id.height_uom_id')
    product_width = fields.Float(related='product_id.width')
    product_width_uom_id = fields.Many2one(related='product_id.width_uom_id')
    product_thickness = fields.Float(related='product_id.thickness')
    product_thickness_uom_id = fields.Many2one(related='product_id.thickness_uom_id')
    prepress_proof_id = fields.Many2one('prepress.proof', string='Prepress Proof',
                                        states={'draft': [('readonly', False)]}, readonly=True)
    height = fields.Float(string='Height', states={'draft': [('readonly', False)]}, readonly=True)
    height_uom_id = fields.Many2one('uom.uom', string="Height Unit of Measure",
                                    default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    width = fields.Float(string='Width', states={'draft': [('readonly', False)]}, readonly=True)
    width_uom_id = fields.Many2one('uom.uom', string="Width unit of Measure",
                                   default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    type_format = fields.Selection([('optimal_format', 'Optimal format'),
                                    ('big_format', 'Big format'),
                                    ('alternate_format', 'Alternate Format')], string="Format",
                                   states={'draft': [('readonly', False)]}, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)
    lineation = fields.Many2one('prepress.plate.lineature', string='Lineation', states={'draft': [('readonly', False)]},
                                readonly=True)
    frame_type_id = fields.Many2one('prepress.plate.frame.type', string='Frame type',
                                    states={'draft': [('readonly', False)]},
                                    readonly=True)
    point_form_id = fields.Many2one('prepress.plate.point.form', string='Point forme',
                                    states={'draft': [('readonly', False)]},
                                    readonly=True)
    sub_product_ids = fields.One2many('prepress.plate.sub.product', 'plate_id', string='Sub-products',
                                      states={'draft': [('readonly', False)]}, readonly=True)
    calibration = fields.Boolean(string='Calibration', states={'draft': [('readonly', False)]}, readonly=True)
    cut_height = fields.Float(string='Mounting height', states={'draft': [('readonly', False)]}, readonly=True)
    cut_height_uom_id = fields.Many2one('uom.uom', string="Mounting Height Unit of Measure",
                                        default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    cut_width = fields.Float(string='Mounting width', states={'draft': [('readonly', False)]}, readonly=True)
    cut_width_uom_id = fields.Many2one('uom.uom', string="Mounting Width Unit of Measure",
                                       default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    tag_ids = fields.Many2many('prepress.tags', relation='prepress_plate_tags_rel', string='Tags'
                               , states={'draft': [('readonly', False)]}, readonly=True)
    screen_angle_lines = fields.One2many('prepress.plate.screen.angle', 'plate_id',
                                         states={'draft': [('readonly', False)]}, readonly=True)
    plate_varnish_id = fields.Many2one('prepress.plate',string='Varnish plate',domain=[('product_plate_type','=','plate_varnish'),
                                                                                       ('state','=','validated')],
                                       states={'draft': [('readonly', False)]}, readonly=True)


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.product_id and self.product_id.partner_id != self.partner_id:
            self.update({'product_id': False, 'sub_product_ids': False})

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self._update_prepress_proof()
        self.update({'cutting_die_id': False})

    @api.onchange('prepress_proof_id')
    def _onchange_prepress_proof_id(self):
        self._update_screen_angle_lines()

    @api.onchange('cutting_die_id')
    def _onchange_cutting_die_id(self):
        if self.cutting_die_id:
            self.update({'exposure_nbr': self.cutting_die_id.exposure_nbr,
                         'cut_height': self.cutting_die_id.cut_height,
                         'cut_height_uom_id': self.cut_height_uom_id and self.cut_height_uom_id.id or False,
                         'cut_width': self.cutting_die_id.cut_width,
                         'cut_width_uom_id': self.cutting_die_id.cut_width_uom_id and self.cutting_die_id.cut_width_uom_id.id or False})

    def _update_prepress_proof(self):
        if not self.product_id:
            return
        prepress_proof = self.env['prepress.proof']._get_by_product_id(self.product_id.id,
                                                                       excluded_states=('in_progress','quarantined','cancel'),
                                                                       limit=1)
        self.update({'prepress_proof_id': prepress_proof and prepress_proof.id or False})

    def _update_screen_angle_lines(self):
        self.screen_angle_lines = False
        screen_angle_lines = []
        if self.prepress_proof_id:
            for color_line in self.prepress_proof_id.color_ids:
                screen_angle_lines.append((0, 0, {
                    'color_id': color_line.color_id.id,
                    'color_code': color_line.color_code
                }))
        self.update({'screen_angle_lines': screen_angle_lines})

    def action_confirm(self):
        self._flash_related_prepress_proofs()
        return self._action_confirm()

    def _flash_related_prepress_proofs(self):
        for each in self.filtered(lambda pl:pl.product_plate_type == 'plate_ctp'):
            each.prepress_proof_id.action_flash()
            each.sub_product_ids.mapped("prepress_proof_id").action_flash()


    def _action_confirm(self):
        self._check_validated_plate()
        for each in self:
            each._set_name_by_sequence()
        self.write({'state': 'validated'})



    def _check_validated_plate(self):
        for each in self:
            if each.state != 'draft':
                raise ValidationError(_("Can not validate non draft Plates!"))
            if each.product_plate_type == 'plate_varnish' and not each.cutting_die_id:
                raise ValidationError(_("Cutting Die is required in varnish Plate!"))
            elif each.product_plate_type == 'plate_ctp' and not each.product_id:
                raise ValidationError(_("Product is required in CTP Plate!"))
            elif each.product_plate_type == 'plate_ctp' and not each.prepress_proof_id:
                raise ValidationError(_("Prepress Proof is required in CTP Plate!"))
            elif each.product_plate_type == 'plate_ctp' and each.prepress_proof_id.id != self.env[
                'prepress.proof']._get_by_product(each.product_id).id:
                raise ValidationError(
                    _("Prepress Proof has been changed,Please refresh the Prepress proof by re-selecting the product!"))

    def _set_name_by_sequence(self):
        self.ensure_one()
        if self.name != "New":
            return
        if self._sequence_dynamic_installed():
            # FIXME:We have to test this in important data volume
            dynamic_prefix_fields = self._build_dynamic_prefix_fields()
            name = self.env['ir.sequence'].with_context(dynamic_prefix_fields=dynamic_prefix_fields).next_by_code(
                DEFAULT_CODE_PLATE)
        else:
            name = self.env['ir.sequence'].next_by_code(DEFAULT_CODE_PLATE)
        self.name = name

    @api.model
    def _sequence_dynamic_installed(self):
        "This method return True if the sequence_dynamic module is installed"
        return 'sequence_dynamic' in self.env['ir.module.module']._installed().keys()

    def _build_dynamic_prefix_fields(self):
        self.ensure_one()
        vals = {}
        for field_name, _ in self._fields.items():
            vals.update({field_name: getattr(self, field_name)})
        return vals

    def action_cancel(self):
        for each in self:
            if each.state != 'validated':
                raise ValidationError(_("Only validated Plates can be cancelled!"))
        return self._action_cancel()

    def _action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reset(self):
        for each in self:
            if each.state != 'validated':
                raise ValidationError(_("Only validated Plates can be reset!"))
        return self._action_reset()

    def _action_reset(self):
        self.write({'state': 'draft'})

    def unlink(self):
        for each in self:
            if each.state == 'validated':
                raise ValidationError(_("Can not remove validated Plate!"))
        return super(PrepressPlate, self).unlink()

    @api.constrains('height', 'width')
    def _check_dimensions(self):
        for each in self:
            if float_compare(each.height, 0, precision_rounding=each.height_uom_id.rounding) <= 0 or float_compare(
                    each.width, 0, precision_rounding=each.width_uom_id.rounding) <= 0:
                raise ValidationError(_("Height/Width must be more than 0"))

    @api.constrains('exposure_nbr', 'cutting_die_id')
    def _check_exposure_nbr(self):
        for each in self.filtered(lambda e: e.cutting_die_id and e.exposure_nbr):
            if each.exposure_nbr > each.cutting_die_id.exposure_nbr:
                raise ValidationError(_("Exposure Nbr must be less than or equal to Cutting die Exposure Nbr"))

    @api.constrains('product_id', 'sub_product_ids')
    def _check_sub_product_ids(self):
        for each in self.filtered(lambda e: e.sub_product_ids):
            if each.product_id.id in each.sub_product_ids.mapped("product_id").ids or len(
                    each.sub_product_ids.mapped("product_id")) != len(each.sub_product_ids):
                raise ValidationError(_("Can not put the same product many times in the same CTP plate"))


class PrepressPlateSubProduct(models.Model):
    _name = 'prepress.plate.sub.product'

    plate_id = fields.Many2one('prepress.plate', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', states={'draft': [('readonly', False)]},
                                 readonly=True, domain=[('type', '=', 'product')], required=True)
    prepress_proof_id = fields.Many2one('prepress.proof', string='Prepress Proof',
                                        states={'draft': [('readonly', False)]}, readonly=True, required=True)
    state = fields.Selection(related='plate_id.state')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self._update_prepress_proof()

    def _update_prepress_proof(self):
        if not self.product_id:
            return
        prepress_proof = self.env['prepress.proof']._get_by_product(self.product_id)
        self.update({'prepress_proof_id': prepress_proof and prepress_proof.id or False})


class PrepressPlateFrameType(models.Model):
    _name = 'prepress.plate.frame.type'
    _description = 'Plate Frame type'
    # fields
    # stored fields
    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)


class PrepressPlateFrameType(models.Model):
    _name = 'prepress.plate.point.form'
    _description = 'Plate Point form'
    # fields
    # stored fields
    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)


class PrepressPlateScreenAngle(models.Model):
    _name = 'prepress.plate.screen.angle'

    plate_id = fields.Many2one("prepress.plate", ondelete='cascade')
    color_id = fields.Many2one('product.product', string='Reference', required=True,
                               domain=[('color_code', '!=', False), ('type', '=', 'product')])
    color_code = fields.Char(string='Color', compute='_compute_color_code', required=True, store=True, readonly=False)
    screen_angle = fields.Float(string='Screen angle')


class PrepressPlateLineature(models.Model):
    _name = 'prepress.plate.lineature'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
