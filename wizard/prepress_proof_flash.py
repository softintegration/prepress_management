# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.tools.date_utils import add
from odoo.exceptions import ValidationError


class PrepressProofFlash(models.TransientModel):
    _name = 'prepress.proof.flash'
    _description = 'Flash'

    product_id = fields.Many2one('product.product',string='Product')
    height = fields.Float(string='Height',related='product_id.height')
    height_uom_id = fields.Many2one('uom.uom', string="Height Unit of Measure",related='product_id.height_uom_id')
    width = fields.Float(string='Width',related='product_id.width')
    width_uom_id = fields.Many2one('uom.uom', string="Width unit of Measure",related='product_id.width_uom_id')
    thickness = fields.Float(string='Thickness',related='product_id.thickness')
    thickness_uom_id = fields.Many2one('uom.uom', string="Thickness Unit of Measure",related='product_id.thickness_uom_id')
    partner_id = fields.Many2one('res.partner',string='Customer')

    flash_date = fields.Date(string='Flash Date', default=fields.Date.context_today, required=True)
    cutting_die_id = fields.Many2one('prepress.cutting.die', string="Cutting Die")
    prepress_plate_ctp_id = fields.Many2one('prepress.plate', string="CTP Plate")
    prepress_plate_varnish_id = fields.Many2one('prepress.plate', string="Varnish Plate")
    excluded_plate_ctp_ids = fields.Many2many('prepress.plate')

    @api.onchange('cutting_die_id')
    def on_change_cutting_die_id(self):
        self.prepress_plate_varnish_id = False

    def apply(self):
        self._check_before_appy()
        prepress_proof_id = self.env.context.get("active_id")
        prepress_proof = self.env['prepress.proof'].browse(prepress_proof_id)
        prepress_proof.action_flash(self.flash_date,self.cutting_die_id,self.prepress_plate_ctp_id,self.prepress_plate_varnish_id)


    def _check_before_appy(self):
        if not self.cutting_die_id:
            raise ValidationError(_("Cutting Die is required!"))
        if not self.prepress_plate_ctp_id:
            raise ValidationError(_("CTP Plate is required!"))