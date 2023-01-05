# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from random import randint

class PrepressTags(models.Model):
    """ Tags of project's tasks """
    _name = "prepress.tags"
    _description = "Prepress Tags"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    model = fields.Char('Model',required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name,model)', "Tag name already exists!"),
    ]






