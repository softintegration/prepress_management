# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PrepressType(models.Model):
    _name = 'prepress.type'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)


    @api.model
    def _default_types(self):
        type_case = self.env.ref('prepress_management.prepress_type_case')
        type_leaflet = self.env.ref('prepress_management.prepress_type_leaflet')
        return [type_case.id,type_leaflet.id]


    """def write(self, vals):
        if 'code' in vals:
            if any(prepress_type.id in self._default_types() for prepress_type in self):
                raise ValidationError(_("Can not update code of default type!"))
        return super(PrepressType,self).write(vals)

    def unlink(self):
        for each in self:
            if each.id in self._default_types():
                raise ValidationError(_("Can not remove default type!"))
        return super(PrepressType,self).unlink()"""






