# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    prepress_type = fields.Many2one('prepress.type', string='Type')
    prepress_proof_next_version = fields.Integer(string='Prepress proof next version', readonly=True, default=1)
    prepress_proofs_count = fields.Integer(compute='_compute_prepress_proofs_count')


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



class PrepressType(models.Model):
    _name = 'prepress.type'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')






