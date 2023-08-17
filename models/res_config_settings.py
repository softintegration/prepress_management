# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_prepress_proof_advanced_cancel = fields.Boolean(string='Prepress proof advanced cancel procedure',)
    product_id_categ = fields.Many2one('product.category', string='Cutting die product default category',
                                               related='company_id.product_id_categ',readonly=False)
