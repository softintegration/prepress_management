# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from random import randint
DEFAULT_CODE_CUTTING_DIE = "prepress.cutting.die"


class PrepressCuttingDie(models.Model):
    _name = 'prepress.cutting.die'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'cancel.motif.class']
    _description = "Cutting Die"

    name = fields.Char(string='Name', required=True, copy=False, index=True, default='New')
    state = fields.Selection([('draft', 'Draft'),
                              ('validated', 'Validated'),
                              ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False,
                             tracking=True, default='draft')
    partner_ids = fields.Many2many('res.partner', 'prepress_cutting_die_res_partner', string='Customers',
                                   states={'draft': [('readonly', False)]}, readonly=True,
                                   domain=[('customer_rank', '>', 0)],
                                   required=True)
    prepress_type = fields.Many2one('prepress.type', string='Type', states={'draft': [('readonly', False)]},
                                    readonly=True, required=True)
    prepress_type_code = fields.Char(related='prepress_type.code')
    height = fields.Float(string='Height', states={'draft': [('readonly', False)]}, readonly=True)
    height_uom_id = fields.Many2one('uom.uom', string="Height Unit of Measure",
                                    default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    width = fields.Float(string='Width', states={'draft': [('readonly', False)]}, readonly=True)
    width_uom_id = fields.Many2one('uom.uom', string="Width unit of Measure",
                                   default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    thickness = fields.Float(string='Thickness', states={'draft': [('readonly', False)]}, readonly=True)
    thickness_uom_id = fields.Many2one('uom.uom', string="Thickness Unit of Measure",
                                       default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    mounting_type_id = fields.Many2one('prepress.cutting.die.mounting.type', string='Mounting type',
                                       states={'draft': [('readonly', False)]}, readonly=True,required=True)
    format_type_id = fields.Many2one('prepress.cutting.die.format.type', string='Format type',
                                     states={'draft': [('readonly', False)]}, readonly=True)
    cut_height = fields.Float(string='Mounting height', states={'draft': [('readonly', False)]}, readonly=True)
    cut_height_uom_id = fields.Many2one('uom.uom', string="Mounting Height Unit of Measure",
                                        default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    cut_width = fields.Float(string='Mounting width', states={'draft': [('readonly', False)]}, readonly=True)
    cut_width_uom_id = fields.Many2one('uom.uom', string="Mounting Width Unit of Measure",
                                       default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    fin_height = fields.Float(string='Finishing height', states={'draft': [('readonly', False)]}, readonly=True)
    fin_height_uom_id = fields.Many2one('uom.uom', string="Fin Height Unit of Measure",
                                        default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    fin_width = fields.Float(string='Finishing width', states={'draft': [('readonly', False)]}, readonly=True)
    fin_width_uom_id = fields.Many2one('uom.uom', string="Fin Width Unit of Measure",
                                       default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    exposure_nbr = fields.Integer('Exposure Nbr', states={'draft': [('readonly', False)]}, readonly=True)
    cutting_count = fields.Integer('Cutting count', states={'draft': [('readonly', False)]}, readonly=True)
    with_braille = fields.Boolean(string='With braille', states={'draft': [('readonly', False)]}, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)
    shelling = fields.Boolean(string="Shelling",states={'draft': [('readonly', False)]}, readonly=True,default=False)
    creasing_rule = fields.Float(string='Creasing rule 1 exposure', states={'draft': [('readonly', False)]},
                                 readonly=True)
    creasing_rule_uom_id = fields.Many2one('uom.uom', string="Creasing Rule Unit of Measure",
                                           default=lambda self: self.env.ref('uom.product_uom_cm'))
    dummy = fields.Html(string='Dummy', states={'draft': [('readonly', False)]}, readonly=True)
    tag_ids = fields.Many2many('prepress.tags', relation='prepress_cutting_die_tags_rel', string='Tags',
                               states={'draft': [('readonly', False)]}, readonly=True)
    locked = fields.Boolean(string='Locked', help="If the cutting die is locked we can't edit Customers",
                            default=False)

    def action_confirm(self):
        return self._action_confirm()

    def _action_confirm(self):
        self._check_validated_cutting_die()
        for each in self:
            each._set_name_by_sequence()
        self.write({'state': 'validated','locked': True})

    def _check_validated_cutting_die(self):
        for each in self:
            if each.state != 'draft':
                raise ValidationError(_("Can not validate non draft Cutting dies!"))

    def _set_name_by_sequence(self):
        self.ensure_one()
        if self.name != "New":
            return
        if self._sequence_dynamic_installed():
            # FIXME:We have to test this in important data volume
            dynamic_prefix_fields = self._build_dynamic_prefix_fields()
            name = self.env['ir.sequence'].with_context(dynamic_prefix_fields=dynamic_prefix_fields).next_by_code(
                DEFAULT_CODE_CUTTING_DIE)
        else:
            name = self.env['ir.sequence'].next_by_code(DEFAULT_CODE_CUTTING_DIE)
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
                raise ValidationError(_("Only validated Cutting dies can be cancelled!"))
        return self._action_cancel()

    def _action_cancel(self):
        self.write({'state': 'cancel'})


    def action_reset(self):
        for each in self:
            if each.state != 'validated':
                raise ValidationError(_("Only validated Cutting dies can be reset!"))
        return self._action_reset()

    def _action_reset(self):
        self.write({'state': 'draft'})


    def action_lock(self):
        self.write({'locked': True})

    def action_unlock(self):
        self.write({'locked': False})


    @api.constrains('exposure_nbr')
    def _check_exposure_nbr(self):
        for each in self:
            if each.exposure_nbr < 1:
                raise ValidationError(_("Exposure Nbr must be strictly positive"))

class CuttingDieMountingType(models.Model):
    _name = 'prepress.cutting.die.mounting.type'
    _description = 'Mounting type'
    # fields
    # stored fields
    name = fields.Char(string='Nom', required=True)
    both_sides = fields.Boolean(string='Both sides', default=False)
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)


class CuttingDieFormatType(models.Model):
    _name = 'prepress.cutting.die.format.type'
    _description = 'Format type'

    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    dummy = fields.Html(string='Dummy')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)

