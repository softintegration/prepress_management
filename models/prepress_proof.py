# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from random import randint


class PrepressProof(models.Model):
    _name = 'prepress.proof'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'cancel.motif.class']
    _description = "Prepress proof"
    _order = "creation_date desc"

    name = fields.Char(string='Name', required=True, copy=False, index=True, default='New')
    client_ref = fields.Char(string='Customer Prepress proof reference',
                             states={'in_progress': [('readonly', False)]}, readonly=True, required=True,
                             copy=False, index=True)
    state = fields.Selection([('in_progress', 'In progress'),
                              ('validated', 'Validated'),
                              ('flashed', 'Flashed'),
                              ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False,
                             tracking=True, default='in_progress')
    partner_id = fields.Many2one('res.partner', required=True, string=u'Customer',
                                 states={'in_progress': [('readonly', False)]}, readonly=True, index=True,
                                 domain=[('customer_rank', '>', 0)])
    product_id = fields.Many2one('product.product', string=u'Product', required=True,
                                 states={'in_progress': [('readonly', False)]}, readonly=True, copy=False, index=True)
    prepress_type = fields.Many2one('prepress.type', string='Type', states={'in_progress': [('readonly', False)]},
                                    readonly=True)
    product_height = fields.Float(string='Height', states={'in_progress': [('readonly', False)]}, readonly=True)
    product_height_uom_id = fields.Many2one('uom.uom', string="Height Unit of Measure",
                                            default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    product_width = fields.Float(string='Width', states={'in_progress': [('readonly', False)]}, readonly=True)
    product_width_uom_id = fields.Many2one('uom.uom', string="Width unit of Measure",
                                           default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    product_thickness = fields.Float(string='Thickness', states={'in_progress': [('readonly', False)]}, readonly=True)
    product_thickness_uom_id = fields.Many2one('uom.uom', string="Thickness Unit of Measure",
                                               default=lambda self: self.env.ref('uom.product_uom_millimeter'))
    product_weight = fields.Integer(string='Weight', states={'in_progress': [('readonly', False)]}, readonly=True)
    product_weight_uom_id = fields.Many2one('uom.uom', string="Weight Unit of Measure",
                                            default=lambda self: self.env.ref('uom.product_uom_gram'))
    creation_date = fields.Date(string='Creation date', states={'in_progress': [('readonly', False)]}, readonly=True)
    confirm_date = fields.Date(string='Confirm date', states={'in_progress': [('readonly', False)]}, readonly=True)
    update_date = fields.Date(string='Update date', states={'in_progress': [('readonly', False)]}, readonly=True)
    cancel_date = fields.Date(string='Cancel date', states={'in_progress': [('readonly', False)]}, readonly=True)
    color_ids = fields.One2many('prepress.proof.color', 'prepress_proof_id', string="Colors",
                                states={'in_progress': [('readonly', False)]}, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)
    note = fields.Html('Note', states={'in_progress': [('readonly', False)]}, readonly=True)
    dummy = fields.Html('Dummy', states={'in_progress': [('readonly', False)]}, readonly=True)
    tag_ids = fields.Many2many('prepress.proof.tags', relation='prepress_proof_prepress_proof_tags_rel', string='Tags',
                               states={'in_progress': [('readonly', False)]}, readonly=True)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.product_id and self.product_id.partner_id != self.partner_id:
            self.update({'product_id': False})

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.update({
            'prepress_type': self.product_id and self.product_id.prepress_type and self.product_id.prepress_type.id or False})

    def action_confirm(self):
        return self._action_confirm()

    def _action_confirm(self):
        self._check_validated_prepress_proofs()
        self._update_prepress_proof_version()
        self.write({'state': 'validated'})

    def action_flash(self):
        return self._action_flash()

    def _action_flash(self):
        self.write({'state': 'flashed'})

    def action_cancel(self):
        return self._action_cancel()

    def _action_cancel(self):
        self.write({'state': 'cancel'})

    def _update_prepress_proof_version(self):
        for each in self:
            each.product_id._increment_prepress_proof_version()

    @api.model
    def _get_by_product_id(self, product_id, count=False):
        """:param : product_id : ID of the product"""
        domain = [('product_id', '=', product_id)]
        if count:
            return self.search_count(domain)
        else:
            return self.search(domain)

    @api.model
    def _get_by_product_tmpl_id(self, product_tmpl_id, count=False):
        """:param : product_tmpl_id : ID of the product template"""
        product_variant_ids = self.env['product.template'].browse(product_tmpl_id).product_variant_ids
        domain = [('product_id', 'in', product_variant_ids.ids)]
        if count:
            return self.search_count(domain)
        else:
            return self.search(domain)

    @api.model
    def create(self, vals):
        self._check_in_progress_prepress_proofs(vals)
        vals['name'] = self.env['ir.sequence'].with_context(dynamic_prefix_fields=vals).next_by_code('prepress.proof')
        prepress_proofs = super(PrepressProof, self).create(vals)
        return prepress_proofs

    # FIXME:This 2 checks must be tested with > 100000 Prepress Proof for evaluating it's performance
    @api.model
    def _check_in_progress_prepress_proofs(self, vals):
        domain = [('state', '=', 'in_progress'), ('product_id', '=', vals["product_id"]),
                  ('company_id','=', vals.get('company_id', self.env.company.id))]
        if self.search_count(domain) > 0:
            raise ValidationError(_("Only one in progress Prepress Proof is authorised by product!"))

    def _check_validated_prepress_proofs(self):
        domain = [('state', 'in', ('validated', 'flashed')), ('product_id', 'in', self.mapped("product_id").ids)]
        if self.search_count(domain) > 0:
            raise ValidationError(_("Only one Validated/Flashed Prepress Proof is authorised by product!"))


class PrepressProofColor(models.Model):
    _name = 'prepress.proof.color'

    prepress_proof_id = fields.Many2one('prepress.proof', ondelete='cascade', index=True, required=True)
    sequence = fields.Integer(string='Sequence')
    color_id = fields.Many2one('product.product', string='Reference', required=True)
    color_code = fields.Char(string='Color', required=True, store=True)
    rate = fields.Float(string='Rate (%)')


class PrepressProofTags(models.Model):
    """ Tags of project's tasks """
    _name = "prepress.proof.tags"
    _description = "Prepress proof Tags"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
