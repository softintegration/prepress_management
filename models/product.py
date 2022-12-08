# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _increment_prepress_proof_version(self):
        return self.mapped("product_tmpl_id")._increment_prepress_proof_version()
    

