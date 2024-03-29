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
    gram_weight_type = fields.Selection(related='product_id.gram_weight_type')
    color_cpt = fields.Integer(string='Number of Colors', states={'in_progress': [('readonly', False)]}, readonly=True)
    prepress_type = fields.Many2one('prepress.type', string='Type', states={'in_progress': [('readonly', False)]},
                                    readonly=True)
    prepress_type_code = fields.Char(related='prepress_type.code')
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
    product_gram_weight_type = fields.Selection(related='product_id.gram_weight_type',store=True)
    product_default_gram_weight = fields.Integer(string='Default weight',related='product_id.default_gram_weight',
                                         states={'in_progress': [('readonly', False)]}, readonly=True, store=True)
    product_gram_weight_min = fields.Integer(string='Min weight',related='product_id.gram_weight_min',
                                         states={'in_progress': [('readonly', False)]}, readonly=True, store=True)
    product_gram_weight_max = fields.Integer(string='Max weight',related='product_id.gram_weight_max',
                                         states={'in_progress': [('readonly', False)]}, readonly=True, store=True)
    product_gram_weight = fields.Integer(string='Weight', related='product_id.gram_weight',
                                         states={'in_progress': [('readonly', False)]}, readonly=True, store=True)
    product_gram_weight_uom_id = fields.Many2one('uom.uom', related='product_id.gram_weight_uom_id',
                                                 string="Weight Unit of Measure",
                                                 default=lambda self: self.env.ref('uom.product_uom_gram'), store=True)
    gram_weight_tolerance = fields.Integer(string='Weight tolerance',related='product_id.gram_weight_tolerance',
                                           store=True)
    notice_type = fields.Selection(string='Type of notice', related='product_id.notice_type', store=True)
    folding_dimension = fields.Char(string='Folding dimension', related='product_id.folding_dimension', store=True)
    with_braille = fields.Boolean(string='With braille', related='product_id.with_braille', store=True)
    creation_date = fields.Date(string='Creation date', states={'in_progress': [('readonly', False)]}, readonly=True,
                                default=lambda self: fields.Datetime.now())
    confirm_date = fields.Date(string='Confirm date', states={'in_progress': [('readonly', False)]}, readonly=True)
    update_date = fields.Date(string='Update date', states={'in_progress': [('readonly', False)]}, readonly=True)
    cancel_date = fields.Date(string='Cancel date', states={'in_progress': [('readonly', False)]}, readonly=True)
    color_ids = fields.One2many('prepress.proof.color', 'prepress_proof_id', string="Colors")
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
    prepress_plates_ids_count = fields.Integer(compute='_compute_prepress_plates_ids_count')
    customer_signatures = fields.One2many('prepress.proof.customer.signature', 'prepress_proof_id')
    is_sent = fields.Boolean(string='Already sent by mail',default=False)
    locked = fields.Boolean(string='Locked', help="If the prepress proof is locked,no field can be edited",
                            default=False,track_visibility=True)

    def action_lock(self):
        self._action_lock()

    def action_unlock(self):
        self._action_unlock()

    def _action_lock(self):
        self.write({'locked': True})

    def _action_unlock(self):
        self.write({'locked': False})

    def _check_validity_for_product(self, product_id):
        current_prepress_proof = self._get_by_product(product_id)
        return current_prepress_proof == self

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.product_id and self.product_id.partner_id != self.partner_id:
            self.update({'product_id': False})

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.update({
            'prepress_type': self.product_id and self.product_id.prepress_type and self.product_id.prepress_type.id or False})
        self.update({'color_cpt': self.product_id.color_cpt})

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

    def _get_related_prepress_plates_domain(self,sub_product_plates=[]):
        return ['|',('prepress_proof_id', 'in', self.ids),('id','in',sub_product_plates), ('state', 'in', ('validated','cancel')),
                ('product_plate_type', '=', 'plate_ctp')]

    def _get_related_prepress_plates(self):
        return self.env['prepress.plate'].search(self._get_related_prepress_plates_domain(self._get_sub_product_plates().ids))

    def show_prepress_plates(self):
        self.ensure_one()
        # we have to put the ctp plates whose proof is attached to the sub-products
        domain = self._get_related_prepress_plates_domain(self._get_sub_product_plates().ids)
        return {
            'name': _('Plate CTP'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('prepress_management.view_prepress_plate_ctp_tree').id, 'tree'),
                      (self.env.ref('prepress_management.view_prepress_plate_ctp_form').id, 'form')],
            'res_model': 'prepress.plate',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
        }

    def _get_sub_product_plates(self):
        return self.env['prepress.plate.sub.product'].search([('prepress_proof_id','in',self.ids)]).mapped("plate_id")

    def _compute_prepress_plates_ids_count(self):
        for each in self:
            each.prepress_plates_ids_count = len(each._get_related_prepress_plates())

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
            'domain': [('id', 'in', self.quarantined_history_ids.ids)]
        }

    def action_confirm(self):
        self.sudo().action_lock()
        self._check_validated_prepress_proofs()
        self._update_prepress_proof_version()
        return self._action_confirm()

    def _action_confirm(self):
        self.write({'state': 'validated'})

    def __action_flash(self, flash_date, cutting_die, prepress_plate_ctp, prepress_plate_varnish):
        flash_line = self._prepare_flash_line(flash_date, cutting_die, prepress_plate_ctp, prepress_plate_varnish)
        self.env['prepress.proof.flash.line'].create(flash_line)
        self.incr_flash_cpt()
        if self.state != 'flashed':
            return self._action_flash()

    def action_flash(self):
        proofs_to_flash = self.filtered(lambda pp:pp.state not in ('flashed','quarantined'))
        for each in proofs_to_flash:
            each.incr_flash_cpt()
        return proofs_to_flash._action_flash()

    def incr_flash_cpt(self):
        self.ensure_one()
        self.write({'flash_cpt': self.flash_cpt + 1})

    def _prepare_flash_line(self, flash_date, cutting_die, prepress_plate_ctp, prepress_plate_varnish):
        return {
            'prepress_proof_id': self.id,
            'flash_date': flash_date,
            'cutting_die_id': cutting_die.id,
            'prepress_plate_ctp_id': prepress_plate_ctp and prepress_plate_ctp.id or False,
            'exposure_nbr': prepress_plate_ctp and prepress_plate_ctp.exposure_nbr,
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
        self._check_cancel()
        return self._action_cancel()

    def _check_cancel(self):
        self._check_related_plates_state()

    def _check_related_plates_state(self):
        for each in self:
            plates_states = each._get_related_prepress_plates().mapped("state")
            if plates_states and (len(set(plates_states)) != 1 or plates_states[0] != 'cancel'):
                raise ValidationError(_("All related CTP plates must be cancelled!"))


    def _action_cancel(self):
        self.write({'state': 'cancel'})

    def action_quarantine(self, quarantined_motif, date=False):
        self.quarantine_check()
        # we have to register the current state to know how to return
        self._register_current_state()
        self._register_quarantine_history(quarantined_motif, date=date)
        self._action_quarantine()

    def _register_quarantine_history(self, quarantined_motif, date=False):
        for each in self:
            self.env['prepress.proof.quarantined.history'].create({
                'prepress_proof_id': each.id,
                'quarantined_motif': quarantined_motif.name,
                'quarantined_motif_description': quarantined_motif.description,
                'quarantined_date': date and date or fields.Datetime.now()
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
                raise ValidationError(
                    _("Can not put the Prepress Proof %s in quarantine,you have to check the state!") % (each.name))

    def _update_prepress_proof_version(self):
        for each in self:
            each.product_id.with_context(force_update=True)._increment_prepress_proof_version()

    @api.constrains('state','color_cpt','color_ids')
    def _check_colors_cpt_coherence(self):
        for each in self:
            if each.state not in ('in_progress','cancel') and each.color_cpt != len(each.color_ids):
                raise ValidationError(
                    _("Number of Colors in product must be the same as the number of colors in Prepress proof,"
                      "The Prepress proofs %s does not respect this rule!") % (
                        ",".join(each.mapped("name"))))

    @api.model
    def _get_by_product_id(self, product_id, count=False,excluded_states=False,limit=False):
        """:param : product_id : ID of the product"""
        domain = [('product_id', '=', product_id)]
        if excluded_states:
            domain.append(('state','not in',excluded_states))
        if count:
            return self.search_count(domain)
        elif limit:
            return self.search(domain,limit=limit)
        else:
            return self.search(domain)

    @api.model
    def _get_by_product_tmpl_id(self, product_tmpl_id, count=False,excluded_states=False,limit=False):
        """:param : product_tmpl_id : ID of the product template"""
        product_variant_ids = self.env['product.template'].browse(product_tmpl_id).product_variant_ids
        domain = [('product_id', 'in', product_variant_ids.ids)]
        if excluded_states:
            domain.append(('state','not in',excluded_states))
        if count:
            return self.search_count(domain)
        elif limit:
            return self.search(domain, limit=limit)
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
        prepress_proof_not_in_progress = self.env['prepress.proof']
        prepress_proof_without_confirm_date = self.env['prepress.proof']
        prepress_proof_with_incoherent_color_nbr = self.env['prepress.proof']
        prepress_proof_with_wrong_color_nbr = self.env['prepress.proof']
        for each in self:
            if each.state != 'in_progress':
                prepress_proof_not_in_progress |= each
            if not each.confirm_date:
                prepress_proof_without_confirm_date |= each
            if each.color_cpt != len(each.color_ids):
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
            raise ValidationError(
                _("Number of Colors in product must be the same as the number of colors in Prepress proof,"
                  "The Prepress proofs %s does not respect this rule!") % (
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

    def action_prepress_proof_send(self):
        self.ensure_one()
        # FIXME:in the template email_template_prepress_proof, we have used the report prepress_proof_report_lbe.action_report_prepress_proof
        # FIXME (suite): this report has to be changed by the good one because the parent module of this report is temporary

        template_id = self.env['ir.model.data']._xmlid_to_res_id('prepress_management.email_template_prepress_proof', raise_if_not_found=False)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': self._name,
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': _('Prepress proof'),
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        self.write({'is_sent': True})
        return super(PrepressProof, self).message_post(**kwargs)


class PrepressProofFlashLine(models.Model):
    _name = 'prepress.proof.flash.line'

    # fields
    prepress_proof_id = fields.Many2one('prepress.proof', required=True, ondelete='cascade')
    cutting_die_id = fields.Many2one('prepress.cutting.die', string="Cutting Die", required=True)
    prepress_plate_ctp_id = fields.Many2one('prepress.plate', string="CTP Plate")
    cut_height = fields.Float(string='Mounting height', related='prepress_plate_ctp_id.cut_height', store=True)
    cut_height_uom_id = fields.Many2one('uom.uom', string="Mounting Height Unit of Measure",
                                        related='prepress_plate_ctp_id.cut_height_uom_id', store=True)
    cut_width = fields.Float(string='Mounting width', related='prepress_plate_ctp_id.cut_width', store=True)
    cut_width_uom_id = fields.Many2one('uom.uom', string="Mounting Width Unit of Measure",
                                       related='prepress_plate_ctp_id.cut_width_uom_id', store=True)
    prepress_plate_varnish_id = fields.Many2one('prepress.plate', string="Varnish Plate")
    is_default = fields.Boolean(string="Default", default=False)
    exposure_nbr = fields.Integer('Exposure Nbr', store=True)

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
            if each.color_id:
                each.color_code = each.color_id.color_code


class PrepressProofCustomerSignature(models.Model):
    _name = 'prepress.proof.customer.signature'

    prepress_proof_id = fields.Many2one('prepress.proof', required=True, ondelete='cascade')
    signed_by = fields.Many2one('res.partner', string='Signed by', required=True)
    function = fields.Char(string='Job Position', related='signed_by.function', store=True)
    signed_on = fields.Datetime('Signed On', help='Date of the signature.', required=True)
    signature = fields.Image('Signature', help='Signature received through the portal.', attachment=True,
                             max_width=1024, max_height=1024)
