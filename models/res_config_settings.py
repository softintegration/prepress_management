# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_prepress_proof_advanced_cancel = fields.Boolean(string='Prepress proof advanced cancel procedure',)
