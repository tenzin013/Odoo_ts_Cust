# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BackDateWizard(models.TransientModel):
    _name = 'back.date.wizard'
    _description = 'Back Date Entry Wizard'

    back_date = fields.Date(
        string='Back Date',
        required=True,
        default=fields.Date.today,
        help='This date will be applied to all selected records.',
    )
    model_name = fields.Char(string='Model', readonly=True)
    record_ids = fields.Char(string='Record IDs', readonly=True)
    apply_to_related = fields.Boolean(
        string='Apply to Related Records',
        default=True,
        help='Also update dates on linked pickings, invoices or journal entries.',
    )
    note = fields.Text(
        string='Note / Reason',
        help='Optional reason for applying a back date (logged in chatter).',
    )

    # ------------------------------------------------------------------ #
    #  Default getter — called from any tree/form action                 #
    # ------------------------------------------------------------------ #
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model', '')
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'model_name': active_model,
            'record_ids': str(active_ids),
        })
        return res

    # ------------------------------------------------------------------ #
    #  Apply                                                              #
    # ------------------------------------------------------------------ #
    @api.model
    def action_open_wizard(self):
        """Called from server actions — opens this wizard as a dialog."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Apply Back Date'),
            'res_model': 'back.date.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_apply(self):
        self.ensure_one()
        if not self.back_date:
            raise UserError(_('Please select a Back Date.'))

        model = self.model_name
        try:
            record_ids = eval(self.record_ids)   # safe — only int list
        except Exception:
            raise UserError(_('Invalid record selection.'))

        records = self.env[model].browse(record_ids)
        if not records:
            raise UserError(_('No records found to update.'))

        back_date = self.back_date
        back_datetime = fields.Datetime.to_datetime(str(back_date) + ' 00:00:00')
        note = self.note or ''

        supported_models = {
            'sale.order',
            'purchase.order',
            'account.move',
            'stock.picking',
        }
        if model not in supported_models:
            raise UserError(_(
                'Back Date Entry is not supported for model "%s".'
            ) % model)

        for rec in records:
            rec.write({'back_date': back_date})
            rec.action_apply_back_date()
            if note:
                rec.message_post(body=_('Back Date Reason: %s') % note)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Back Date Applied'),
                'message': _(
                    'Back date <b>%s</b> applied to %d record(s).'
                ) % (back_date, len(records)),
                'type': 'success',
                'sticky': False,
            },
        }
