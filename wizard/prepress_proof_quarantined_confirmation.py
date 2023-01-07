# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class PrepressProofQuarantinedConfirmation(models.TransientModel):
    _name = 'prepress.proof.quarantined.confirmation'
    _description = 'Quarantined confirmation'

    quarantined_motif_id = fields.Many2one('prepress.proof.quarantined.motif',string='Quarantined motif')

    def apply(self):
        if not self.quarantined_motif_id:
            raise ValidationError(_("Quarantined motif is required!"))
        prepress_proof_id = self.env.context.get("active_id")
        prepress_proof = self.env['prepress.proof'].browse(prepress_proof_id)
        return prepress_proof.action_quarantine(self.quarantined_motif_id)




