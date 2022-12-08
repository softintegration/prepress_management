# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    prepress_type = fields.Many2one('prepress.type',string='Type')


class PrepressType(models.Model):
    _name = 'prepress.type'


    code = fields.Char('Code',required=True)
    name = fields.Char('Name',required=True)
    description = fields.Text('Description')