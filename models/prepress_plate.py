# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from random import randint
DEFAULT_CODE_PLATE = "prepress.plate"


class PrepressPlate(models.Model):
    _name = 'prepress.plate'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'cancel.motif.class']
    _description = "Plate"

    name = fields.Char(string='Name', required=True, copy=False, index=True,
                       states={'draft': [('readonly', False)]},readonly=True,default='New')
    state = fields.Selection([('draft', 'Draft'),
                              ('validated', 'Validated'),
                              ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False,
                             tracking=True, default='draft')
    product_plate_type = fields.Selection([('plate_ctp', 'CTP Plate'),
                                           ('plate_varnish', 'Varnish Plate')], string='Type',
                                          states={'draft': [('readonly', False)]}, readonly=True)
    product_varnish_id = fields.Many2one('product.product',string='Varnish',states={'draft': [('readonly', False)]},
                                         readonly=True)
    cutting_die_id = fields.Many2one('prepress.cutting.die', string="Cutting Die", states={'draft': [('readonly', False)]},
                                     readonly=True)
    exposure_nbr = fields.Integer('Exposure Nbr', states={'draft': [('readonly', False)]}, readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 states={'draft': [('readonly', False)]}, readonly=True,
                                 domain=[('customer_rank', '>', 0), ('parent_id', '=', False)])
    product_id = fields.Many2one('product.product', string='Product', states={'draft': [('readonly', False)]},
                                 readonly=True,domain=[('type', '=', 'product')])
    prepress_proof_id = fields.Many2one('prepress.proof',string='Prepress Proof',states={'draft': [('readonly', False)]}, readonly=True)
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
    lineation = fields.Char(string='Lineation', states={'draft': [('readonly', False)]}, readonly=True)
    frame_type_id = fields.Many2one('prepress.plate.frame.type', string='Frame type', states={'draft': [('readonly', False)]},
                                   readonly=True)
    point_form_id = fields.Many2one('prepress.plate.point.form', string='Point forme', states={'draft': [('readonly', False)]},
                                    readonly=True)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.product_id and self.product_id.partner_id != self.partner_id:
            self.update({'product_id': False})

    @api.onchange('product_id','cutting_die_id')
    def _onchange_product_id(self):
        self._update_prepress_proof()
        if self.cutting_die_id:
            self.update({'exposure_nbr': self.cutting_die_id.exposure_nbr})




    def _update_prepress_proof(self):
        if not self.product_id:
            return
        prepress_proof = self.env['prepress.proof']._get_by_product(self.product_id)
        self.update({'prepress_proof_id': prepress_proof and prepress_proof.id or False})


    def action_confirm(self):
        return self._action_confirm()

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
            elif each.product_plate_type == 'plate_ctp' and each.prepress_proof_id.id != self.env['prepress.proof']._get_by_product(each.product_id).id:
                raise ValidationError(_("Prepress Proof has been changed,Please refresh the Prepress proof by re-selecting the product!"))


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
        for field_name,_ in self._fields.items():
            vals.update({field_name:getattr(self,field_name)})
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

