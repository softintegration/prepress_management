# -*- coding: utf-8 -*- 

from odoo import models,fields,api
from odoo.exceptions import UserError


class Company(models.Model):
    _inherit = "res.company"

    product_id_categ = fields.Many2one('product.category', string='Cutting die product default category')