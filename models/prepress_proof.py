# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from random import randint

QUARANTINE_STATES = ('validated', 'flashed')


class PrepressProof(models.Model):
    _name = 'prepress.proof'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'cancel.motif.class']
    _description = "Prepress proof"
    _order = "creation_date desc"

    name = fields.Char(string='Name', required=True, copy=False, index=True, default='New')
    client_ref = fields.Char(string='Customer Prepress proof reference',
                             states={'in_progress': [('readonly', False)]}, readonly=True, required=True,
                             copy=False, index=True)
    state = fields.Selection([('in_progress', 'In progress'),
                              ('validated', 'Validated'),
                              ('flashed', 'Flashed'),
                              ('quarantined', 'Quarantined'),
                              ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False,
                             tracking=True, default='in_progress')
    partner_id = fields.Many2one('res.partner', required=True, string=u'Customer',
                                 states={'in_progress': [('readonly', False)]}, readonly=True, index=True,
                                 domain=[('customer_rank', '>', 0), ('parent_id', '=', False)])
    product_id = fields.Many2one('product.product', string=u'Product', required=True,
                                 states={'in_progress': [('readonly', False)]}, readonly=True, copy=False, index=True)
    prepress_type = fields.Many2one('prepress.type', string='Type', states={'in_progress': [('readonly', False)]},
                                    readonly=True)
    product_height = fields.Float(string='Height', related='product_id.height',
                                  states={'in_progress': [('readonly', False)]}, readonly=True, store=True)
    product_height_uom_id = fields.Many2one('uom.uom', related='product_id.height_uom_id',
                                            string="Height Unit of Measure",
                                            default=lambda self: self.env.ref('uom.product_uom_millimeter'), store=True)
    product_width = fields.Float(string='Width', related='product_id.width',
                                 states={'in_progress': [('readonly', False)]},
                                 readonly=True, store=True)
    product_width_uom_id = fields.Many2one('uom.uom', related='product_id.width_uom_id', string="Width unit of Measure",
                                           default=lambda self: self.env.ref('uom.product_uom_millimeter'), store=True)
    product_thickness = fields.Float(string='Thickness', related='product_id.thickness',
                                     states={'in_progress': [('readonly', False)]}, readonly=True,
                                     store=True)
    product_thickness_uom_id = fields.Many2one('uom.uom', related='product_id.thickness_uom_id',
                                               string="Thickness Unit of Measure",
                                               default=lambda self: self.env.ref('uom.product_uom_millimeter'),
                                               store=True)
    product_gram_weight = fields.Float(string='Weight', related='product_id.gram_weight',
                                       states={'in_progress': [('readonly', False)]}, readonly=True, store=True)
    product_gram_weight_uom_id = fields.Many2one('uom.uom', related='product_id.gram_weight_uom_id',
                                                 string="Weight Unit of Measure",
                                                 default=lambda self: self.env.ref('uom.product_uom_gram'), store=True)
    creation_date = fields.Date(string='Creation date', states={'in_progress': [('readonly', False)]}, readonly=True,
                                default=lambda self: fields.Datetime.now())
    confirm_date = fields.Date(string='Confirm date', states={'in_progress': [('readonly', False)]}, readonly=True)
    update_date = fields.Date(string='Update date', states={'in_progress': [('readonly', False)]}, readonly=True)
    cancel_date = fields.Date(string='Cancel date', states={'in_progress': [('readonly', False)]}, readonly=True)
    color_ids = fields.One2many('prepress.proof.color', 'prepress_proof_id', string="Colors",
                                states={'in_progress': [('readonly', False)]}, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)
    note = fields.Html('Note', states={'in_progress': [('readonly', False)]}, readonly=True)
    dummy = fields.Html('Dummy', states={'in_progress': [('readonly', False)]}, readonly=True)
    tag_ids = fields.Many2many('prepress.tags', relation='prepress_proof_tags_rel', string='Tags',
                               states={'in_progress': [('readonly', False)]}, readonly=True)
    cancel_motif_name = fields.Char(string='Cancel motif', related='cancel_motif_id.name', store=True, readonly=True)
    cancel_motif_description = fields.Text(string='Cancel motif Details', related='cancel_motif_id.description',
                                           store=True, readonly=True)
    state_before_quarantined = fields.Selection([('validated', 'Validated'),
                                                 ('flashed', 'Flashed')])
    quarantined = fields.Boolean(string='Has been quarantined', default=False)
    quarantined_history_ids = fields.One2many('prepress.proof.quarantined.history', 'prepress_proof_id')
    quarantined_history_ids_count = fields.Integer(compute='_compute_quarantined_history_ids_count')
    flash_line_ids = fields.One2many('prepress.proof.flash.line', 'prepress_proof_id')
    flash_line_ids_count = fields.Integer(compute='_compute_flash_line_ids_count')
    flash_cpt = fields.Integer(string='Flash cpt', default=0)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.product_id and self.product_id.partner_id != self.partner_id:
            self.update({'product_id': False})

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.update({
            'prepress_type': self.product_id and self.product_id.prepress_type and self.product_id.prepress_type.id or False})

    @api.depends('flash_line_ids')
    def _compute_flash_line_ids_count(self):
        for each in self:
            each.flash_line_ids_count = len(each.flash_line_ids)

    def show_flash_lines(self):
        self.ensure_one()
        domain = [('prepress_proof_id', 'in', self.ids)]
        return {
            'name': _('Flash lines'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('prepress_management.prepress_proof_flash_line_tree_view').id, 'tree'),
                      (self.env.ref('prepress_management.prepress_proof_flash_line_form_view').id, 'form')],
            'res_model': 'prepress.proof.flash.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
        }

    @api.depends('quarantined_history_ids')
    def _compute_quarantined_history_ids_count(self):
        for each in self:
            each.quarantined_history_ids_count = len(each.quarantined_history_ids)

    def show_quarantined_history(self):
        self.ensure_one()
        return {
            'name': _('Quarantine history'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('prepress_management.prepress_proof_quarantined_history_tree_view').id, 'tree'),
                      (self.env.ref('prepress_management.prepress_proof_quarantined_history_form_view').id, 'form')],
            'res_model': 'prepress.proof.quarantined.history',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_ids': self.quarantined_history_ids.ids,
        }

    def action_confirm(self):
        return self._action_confirm()

    def _action_confirm(self):
        self._check_validated_prepress_proofs()
        self._update_prepress_proof_version()
        self.write({'state': 'validated'})

    def action_flash(self, flash_date, cutting_die, prepress_plate_ctp, prepress_plate_varnish):
        flash_line = self._prepare_flash_line(flash_date, cutting_die, prepress_plate_ctp, prepress_plate_varnish)
        self.env['prepress.proof.flash.line'].create(flash_line)
        self.incr_flash_cpt()
        if self.state != 'flashed':
            return self._action_flash()

    def incr_flash_cpt(self):
        self.ensure_one()
        self.write({'flash_cpt': self.flash_cpt + 1})

    def _prepare_flash_line(self, flash_date, cutting_die, prepress_plate_ctp, prepress_plate_varnish):
        return {
            'prepress_proof_id': self.id,
            'flash_date': flash_date,
            'cutting_die_id': cutting_die.id,
            'exposure_nbr': cutting_die.exposure_nbr,
            'prepress_plate_ctp_id': prepress_plate_ctp and prepress_plate_ctp.id or False,
            'prepress_plate_varnish_id': prepress_plate_varnish and prepress_plate_varnish.id or False
        }

    def _action_flash(self):
        self.write({'state': 'flashed'})

    def action_cancel_with_motif(self):
        return self.with_context(model=self._name,
                                 model_ids=self.ids,
                                 method='action_cancel',
                                 default_display_cancel_date=True)._action_cancel_motif_wizard()

    def action_cancel(self):
        return self._action_cancel()

    def _action_cancel(self):
        self.write({'state': 'cancel'})

    def action_quarantine(self, quarantined_motif):
        self.quarantine_check()
        # we have to register the current state to know how to return
        self._register_current_state()
        self._register_quarantine_history(quarantined_motif)
        self._action_quarantine()

    def _register_quarantine_history(self, quarantined_motif):
        for each in self:
            self.env['prepress.proof.quarantined.history'].create({
                'prepress_proof_id': each.id,
                'quarantined_motif': quarantined_motif.name,
                'quarantined_motif_description': quarantined_motif.description
            })

    def _action_quarantine(self):
        self.write({'state': 'quarantined', 'quarantined': True})

    def _register_current_state(self):
        for each in self:
            each.write({'state_before_quarantined': each.state})

    def action_reset_from_quarantine(self):
        self._check_reset_from_quarantine()
        self._action_reset_from_quarantine()

    def _action_reset_from_quarantine(self):
        for each in self:
            each.write({'state': each.state_before_quarantined})

    def _check_reset_from_quarantine(self):
        if any(each.state != 'quarantined' for each in self):
            raise UserError(_("Can not reset from quarantined,you have to check the state!"))

    def quarantine_check(self):
        for each in self:
            if each.state not in QUARANTINE_STATES:
                raise UserError(
                    _("Can not put the Prepress Proof %s in quarantine,you have to check the state!") % each.name)

    def _update_prepress_proof_version(self):
        for each in self:
            each.product_id._increment_prepress_proof_version()

    @api.model
    def _get_by_product_id(self, product_id, count=False):
        """:param : product_id : ID of the product"""
        domain = [('product_id', '=', product_id)]
        if count:
            return self.search_count(domain)
        else:
            return self.search(domain)

    @api.model
    def _get_by_product_tmpl_id(self, product_tmpl_id, count=False):
        """:param : product_tmpl_id : ID of the product template"""
        product_variant_ids = self.env['product.template'].browse(product_tmpl_id).product_variant_ids
        domain = [('product_id', 'in', product_variant_ids.ids)]
        if count:
            return self.search_count(domain)
        else:
            return self.search(domain)

    @api.model
    def create(self, vals):
        self._check_in_progress_prepress_proofs(vals)
        vals['name'] = self.env['ir.sequence'].with_context(dynamic_prefix_fields=vals).next_by_code('prepress.proof')
        prepress_proofs = super(PrepressProof, self).create(vals)
        return prepress_proofs

    def unlink(self):
        if any(prepress_proof.state != 'in_progress' for prepress_proof in self):
            raise ValidationError(_("Only in progress Prepress Proofs can be removed!"))
        return super(PrepressProof, self).unlink()

    # FIXME:This 2 checks must be tested with > 100000 Prepress Proof for evaluating it's performance
    @api.model
    def _check_in_progress_prepress_proofs(self, vals):
        domain = [('state', '=', 'in_progress'), ('product_id', '=', vals["product_id"]),
                  ('company_id', '=', vals.get('company_id', self.env.company.id))]
        if self.search_count(domain) > 0:
            raise ValidationError(_("Only one in progress Prepress Proof is authorised by product!"))

    def _check_validated_prepress_proofs(self):
        self._check_prepress_proof_data()
        domain = [('state', 'in', ('validated', 'flashed', 'quarantined')),
                  ('product_id', 'in', self.mapped("product_id").ids)]
        if self.search_count(domain) > 0:
            raise ValidationError(_("Only one Validated/Flashed Prepress Proof is authorised by product!"))

    def _check_prepress_proof_data(self):
        prepress_proof_not_in_progress= self.env['prepress.proof']
        prepress_proof_without_confirm_date = self.env['prepress.proof']
        prepress_proof_with_incoherent_color_nbr = self.env['prepress.proof']
        prepress_proof_with_wrong_color_nbr = self.env['prepress.proof']
        for each in self:
            if each.state != 'in_progress':
                prepress_proof_not_in_progress |= each
            if not each.confirm_date:
                prepress_proof_without_confirm_date |= each
            if each.product_id.color_cpt != len(each.color_ids):
                prepress_proof_with_incoherent_color_nbr |= each
            if len(each.color_ids) != len(each.color_ids.mapped("color_id")):
                prepress_proof_with_wrong_color_nbr |= each
        if prepress_proof_not_in_progress:
            raise ValidationError(
                _("All selected Prepress proof(s) must be in progress,%s are not in progress!") % (
                    ",".join(prepress_proof_not_in_progress.mapped("name"))))
        if prepress_proof_without_confirm_date:
            raise ValidationError(
                _("Confirm date is required,no confirm date has been detected in the prepress proofs %s!") % (
                    ",".join(prepress_proof_without_confirm_date.mapped("name"))))
        if prepress_proof_with_incoherent_color_nbr:
            raise ValidationError(_("Number of Colors in product must be the same as the number of colors in Prepress proof,"
                                    "The Prepress proofs %s does not respect this rule!")% (
                    ",".join(prepress_proof_with_incoherent_color_nbr.mapped("name"))))
        if prepress_proof_with_wrong_color_nbr:
            raise ValidationError(
                _("Can not select the same color many times,please check the colors in %s!") % (
                    ",".join(prepress_proof_with_wrong_color_nbr.mapped("name"))))




    def action_flash_wizard(self):
        ''' Open the prepress.proof.flash wizard to flash the current Prepress Proof.
        :return: An action opening the prepress.proof.flash wizard.
        '''
        self.ensure_one()
        # we have to exclude already select Plate CTPs from being select again
        excluded_plate_ctp_ids = self.flash_line_ids.mapped("prepress_plate_ctp_id").ids
        prepress_proof_flash_wizard_id = self.env['prepress.proof.flash'].create({
            'product_id': self.product_id.id,
            'partner_id': self.partner_id.id,
            'excluded_plate_ctp_ids': [(6, 0, excluded_plate_ctp_ids)]
        })
        return {
            'name': _('Flash Prepress proof'),
            'res_model': 'prepress.proof.flash',
            'view_mode': 'form',
            'context': {
                'active_model': 'prepress.proof',
                'active_ids': self.ids,
            },
            'res_id': prepress_proof_flash_wizard_id.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_quarantine_wizard(self):
        self.ensure_one()
        prepress_proof_quarantined_confirmation_wizard = self.env['prepress.proof.quarantined.confirmation'].create({})
        return {
            'name': _('Quarantine Confirmation'),
            'res_model': 'prepress.proof.quarantined.confirmation',
            'view_mode': 'form',
            'context': {
                'active_model': 'prepress.proof',
                'active_ids': self.ids,
            },
            'res_id': prepress_proof_quarantined_confirmation_wizard.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class PrepressProofFlashLine(models.Model):
    _name = 'prepress.proof.flash.line'

    # fields
    prepress_proof_id = fields.Many2one('prepress.proof', required=True, ondelete='cascade')
    cutting_die_id = fields.Many2one('prepress.cutting.die', string="Cutting Die", required=True)
    prepress_plate_ctp_id = fields.Many2one('prepress.plate', string="CTP Plate")
    prepress_plate_varnish_id = fields.Many2one('prepress.plate', string="Varnish Plate")
    is_default = fields.Boolean(string="Default", default=False)
    exposure_nbr = fields.Integer('Exposure Nbr', related='cutting_die_id.exposure_nbr', store=True)

    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)
    flash_date = fields.Date(string='Flash Date', default=fields.Date.context_today, required=True)

    def unlink(self):
        for each in self:
            if each.prepress_proof_id and each.prepress_proof_id.state in ('validated', 'flashed'):
                raise ValidationError(_("Can not remove flash line of Validated/Flashed Prepress Proof"))
        return super(PrepressProofFlashLine, self).unlink()


class PrepressProofQuarantinedHistory(models.Model):
    _name = 'prepress.proof.quarantined.history'

    prepress_proof_id = fields.Many2one('prepress.proof', required=True, ondelete='cascade')
    quarantined_motif = fields.Char(string='Motif', required=True)
    quarantined_motif_description = fields.Char(string='Motif details')
    quarantined_date = fields.Datetime(string='Quarantined date', default=lambda self: fields.Datetime.now(),
                                       required=True)

    def name_get(self):
        res = []
        for quarantined_history in self:
            res.append((quarantined_history.id, '%s (%s)' % (
            quarantined_history.prepress_proof_id.name, quarantined_history.quarantined_motif)))
        return res


class PrepressProofQuarantinedMotif(models.Model):
    _name = 'prepress.proof.quarantined.motif'

    name = fields.Char(string='Motif', required=True)
    description = fields.Text(string='Motif Detail')


class PrepressProofColor(models.Model):
    _name = 'prepress.proof.color'

    prepress_proof_id = fields.Many2one('prepress.proof', ondelete='cascade', index=True, required=True)
    sequence = fields.Integer(string='Sequence')
    color_id = fields.Many2one('product.product', string='Reference', required=True,
                               domain=[('color_code', '!=', False), ('type', '=', 'product')])
    color_code = fields.Char(string='Color', compute='_compute_color_code', required=True, store=True, readonly=False)
    rate = fields.Float(string='Rate (%)')

    @api.depends('color_id')
    def _compute_color_code(self):
        for each in self:
            if each.color_id and not each.color_code:
                each.color_code = each.color_id.color_code
