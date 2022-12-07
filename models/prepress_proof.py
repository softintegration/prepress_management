# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PrepressProof(models.Model):
    _name = 'prepress.proof'
    _inherit = ['mail.thread', 'mail.activity.mixin','cancel.motif.class']
    _description = "Prepress proof"
    _order = "creation_date desc"

    name = fields.Char(string='Name', required=True, copy=False,index=True,default='New')
    client_ref = fields.Char(string='Customer Prepress proof reference',
                                            states={'in_progress': [('readonly', False)]}, readonly=True, required=True,
                                            copy=False,index=True)
    state = fields.Selection([('in_progress', 'In progress'),
                              ('validated', 'Validated'),
                              ('flashed', 'Flashed'),
                              ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False,
                             tracking=True, default='in_progress')
    partner_id = fields.Many2one('res.partner', required=True, string=u'Customer',
                                 states={'in_progress': [('readonly', False)]}, readonly=True,index=True)
    product_id = fields.Many2one('product.product', string=u'Product', required=True,
                                 states={'in_progress': [('readonly', False)]}, readonly=True, copy=False,index=True)
    #product_type = fields.Many2one()
    product_height = fields.Float(string='Height',states={'in_progress': [('readonly', False)]}, readonly=True)
    product_height_uom_id = fields.Many2one('uom.uom', string="Height Unit of Measure",
                                            default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    product_width = fields.Float(string='Width',states={'in_progress': [('readonly', False)]}, readonly=True)
    product_width_uom_id = fields.Many2one('uom.uom', string="Width unit of Measure",default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    product_thickness = fields.Float(string='Thickness',states={'in_progress': [('readonly', False)]}, readonly=True)
    product_thickness_uom_id = fields.Many2one('uom.uom', string="Thickness Unit of Measure",
                                               default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    product_weight = fields.Integer(string='Weight',states={'in_progress': [('readonly', False)]}, readonly=True)
    product_weight_uom_id = fields.Many2one('uom.uom', string="Weight Unit of Measure",
                                            default=lambda self: self.env.ref('uom.product_uom_gram'))
    creation_date = fields.Date(string='Creation date',states={'in_progress': [('readonly', False)]}, readonly=True)
    confirm_date = fields.Date(string='Confirm date',states={'in_progress': [('readonly', False)]}, readonly=True)
    update_date = fields.Date(string='Update date',states={'in_progress': [('readonly', False)]}, readonly=True)
    cancel_date = fields.Date(string='Cancel date',states={'in_progress': [('readonly', False)]}, readonly=True)
    color_ids = fields.One2many('prepress.proof.color', 'prepress_proof_id', string="Colors",
                                states={'in_progress': [('readonly', False)]}, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,default=lambda s: s.env.company.id, index=True)
    note = fields.Html('Note',states={'in_progress': [('readonly', False)]}, readonly=True)
    dummy = fields.Html('Dummy',states={'in_progress': [('readonly', False)]}, readonly=True)

class PrepressProofColor(models.Model):
    _name = 'prepress.proof.color'

    prepress_proof_id = fields.Many2one('prepress.proof',ondelete='cascade', index=True,required=True)
    sequence = fields.Integer(string='Sequence')
    color_id = fields.Many2one('product.product', string='Reference',required=True)
    color_code = fields.Char(string='Color',required=True,store=True)
    rate = fields.Float(string='Rate (%)')




