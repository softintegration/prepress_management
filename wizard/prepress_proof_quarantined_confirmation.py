# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class PrepressProofQuarantinedConfirmation(models.TransientModel):
    _name = 'prepress.proof.quarantined.confirmation'
    _description = 'Quarantined confirmation'

    quarantined_date = fields.Datetime(string='Quarantined date', default=lambda self: fields.Datetime.now())
    quarantined_motif_id = fields.Many2one('prepress.proof.quarantined.motif',string='Quarantined motif')


    def apply(self):
        if not self.quarantined_motif_id:
            raise ValidationError(_("Quarantined motif is required!"))
        prepress_proof_ids = self.env.context.get("active_ids")
        prepress_proofs = self.env['prepress.proof'].browse(prepress_proof_ids)
        return prepress_proofs.action_quarantine(self.quarantined_motif_id,date=self.quarantined_date)




