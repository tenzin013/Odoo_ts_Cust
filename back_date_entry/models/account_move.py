# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    back_date = fields.Date(
        string='Back Date',
        copy=False,
        tracking=True,
        help='Set a back date to override the journal entry / invoice accounting date.',
    )
    back_date_applied = fields.Boolean(
        string='Back Date Applied',
        copy=False,
        default=False,
        readonly=True,
    )

    @api.onchange('back_date')
    def _onchange_back_date(self):
        if self.back_date and self.back_date > fields.Date.today():
            return {
                'warning': {
                    'title': _('Future Date Warning'),
                    'message': _(
                        'The back date (%s) is in the future.'
                    ) % self.back_date,
                }
            }

    def action_apply_back_date(self):
        """Apply back_date to the account move (invoice/journal entry)."""
        for move in self:
            if not move.back_date:
                raise UserError(_('Please set a Back Date before applying.'))
            if move.state == 'posted':
                raise UserError(_(
                    'Cannot change the date of a posted journal entry (%s). '
                    'Reset it to draft first.'
                ) % move.name)

            back_date = move.back_date

            move.write({
                'invoice_date': back_date,
                'date': back_date,
                'back_date_applied': True,
            })

            move.message_post(
                body=_(
                    'Back Date <b>%s</b> applied. '
                    'Invoice date and accounting date updated.'
                ) % back_date
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Back Date Applied'),
                'message': _('Back date applied to Journal Entry / Invoice(s).'),
                'type': 'success',
                'sticky': False,
            },
        }

    # ------------------------------------------------------------------ #
    #  Override _post to respect back_date when confirming               #
    # ------------------------------------------------------------------ #
    def _post(self, soft=True):
        for move in self:
            if move.back_date and not move.back_date_applied:
                move.write({
                    'invoice_date': move.back_date,
                    'date': move.back_date,
                    'back_date_applied': True,
                })
        return super()._post(soft=soft)
