# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from random import randint

class PrepressCuttingDie(models.Model):
    _name = 'prepress.cutting.die'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'cancel.motif.class']
    _description = "Cutting Die"
    _order = "creation_date desc"

    name = fields.Char(string='Name', required=True, copy=False, index=True, default='New')
    state = fields.Selection([('draft', 'Draft'),
                              ('validated', 'Validated'),
                              ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False,
                             tracking=True, default='in_progress')
    partner_ids = fields.Many2many('res.partner','prepress_cutting_die_res_partner', string='Customers',
                                 states={'draft': [('readonly', False)]}, readonly=True,domain=[('customer_rank', '>', 0)])
    prepress_type = fields.Many2one('prepress.type', string='Type', states={'draft': [('readonly', False)]},
                                    readonly=True)
    height = fields.Float(string='Height', states={'draft': [('readonly', False)]}, readonly=True)
    height_uom_id = fields.Many2one('uom.uom', string="Height Unit of Measure",
                                            default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    width = fields.Float(string='Width', states={'draft': [('readonly', False)]}, readonly=True)
    width_uom_id = fields.Many2one('uom.uom', string="Width unit of Measure",
                                           default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    thickness = fields.Float(string='Thickness', states={'draft': [('readonly', False)]}, readonly=True)
    thickness_uom_id = fields.Many2one('uom.uom', string="Thickness Unit of Measure",
                                               default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    mounting_type_id = fields.Many2one('prepress.cutting.die.mounting.type',string='Mounting type',states={'draft': [('readonly', False)]}, readonly=True)
    format_type_id = fields.Many2one('prepress.cutting.die.format.type',string='Format type',)
    cut_height = fields.Float(string='Mounting height', states={'draft': [('readonly', False)]}, readonly=True)
    cut_height_uom_id = fields.Many2one('uom.uom', string="Cut Height Unit of Measure",
                                    default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    cut_width = fields.Float(string='Mounting width', states={'draft': [('readonly', False)]}, readonly=True)
    cut_width_uom_id = fields.Many2one('uom.uom', string="Cut Width Unit of Measure",
                                        default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    fin_height = fields.Float(string='Finishing height', states={'draft': [('readonly', False)]}, readonly=True)
    fin_height_uom_id = fields.Many2one('uom.uom', string="Fin Height Unit of Measure",
                                        default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    fin_width = fields.Float(string='Finishing width', states={'draft': [('readonly', False)]}, readonly=True)
    fin_width_uom_id = fields.Many2one('uom.uom', string="Fin Width Unit of Measure",
                                       default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    exposure_nbr = fields.Integer('Exposure Nbr',states={'draft': [('readonly', False)]}, readonly=True)
    cutting_count = fields.Integer('Cutting count',states={'draft': [('readonly', False)]}, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)
    auto_finishing = fields.Boolean(string='Auto finishing',states={'draft': [('readonly', False)]}, readonly=True)
    shelling_type = fields.Selection([('manual', 'Manual'),('auto', 'Automatic')], default='manual',
                                     states={'draft': [('readonly', False)]}, readonly=True)
    creasing_rule = fields.Float(string='Creasing rule 1 exposure',states={'draft': [('readonly', False)]}, readonly=True)
    creasing_rule_uom_id = fields.Many2one('uom.uom', string="Creasing Rule Unit of Measure",
                                        default=lambda self: self.env.ref('uom.product_uom_cm'))
