# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    prepress_type = fields.Many2one('prepress.type', string='Type')
    prepress_proof_next_version = fields.Integer(string='Prepress proof next version', readonly=False, default=0)
    update_prepress_proof_next_version = fields.Boolean(compute='_update_prepress_proof_next_version')
    prepress_proofs_count = fields.Integer(compute='_compute_prepress_proofs_count')
    color_cpt = fields.Integer(string='Number of Colors')
    with_braille = fields.Boolean(string='With braille')
    complexity_factor_id = fields.Many2one('complexity.factor', string="Complexity factor")
    both_sides = fields.Boolean(string='Both sides', default=False)
    is_varnish = fields.Boolean(string='Varnish')
    format_type_id = fields.Many2one('prepress.cutting.die.format.type', string='Format type')
    notice_type = fields.Selection([('flat','Flat'),
                                    ('folded','Folded')], string='Type of notice')
    folding_dimension = fields.Char(string='Folding dimension')
    varnish_type = fields.Many2one('product.varnish', string='Varnish type')
    gram_weight = fields.Float(string='Weight')
    gram_weight_uom_id = fields.Many2one('uom.uom', string="Weight unit of Measure",
                                   default=lambda self: self.env.ref('uom.product_uom_gram'))
    color_code = fields.Char(string='Color')


    def _update_prepress_proof_next_version(self):
        for each in self:
            each.update_prepress_proof_next_version = each.user_has_groups('prepress_management.group_prepress_proof_next_version_update')

    def _increment_prepress_proof_version(self):
        for each in self:
            each.prepress_proof_next_version += 1

    def _compute_prepress_proofs_count(self):
        for each in self:
            each.prepress_proofs_count = self.env['prepress.proof']._get_by_product_tmpl_id(each.id,count=True)


    def show_related_prepress_proofs(self):
        self.ensure_one()
        domain = [('id', 'in', self.env['prepress.proof']._get_by_product_tmpl_id(self.id).ids)]
        # Because in Prepress proof the product is related to partner and fltred by theme we have to take this in account in the context
        return {
            'name': _('Prepress proofs'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('prepress_management.view_prepress_proof_tree').id, 'tree'), (False, 'form')],
            'res_model': 'prepress.proof',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            'context': {
                'default_partner_id':self.partner_id.id,
                'default_product_id': self.product_variant_ids.ids[0],
            },
        }




class ComplexityFactor(models.Model):
    _name = 'complexity.factor'
    _rec_name = 'index'

    # fields
    # stored fields
    index = fields.Float(string='Index', required=True)
    rate = fields.Float(string='Rate(%)', required=True, default=0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)


class VarnishType(models.Model):
    _name = 'product.varnish'
    _description = 'Varnish type'

    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)



