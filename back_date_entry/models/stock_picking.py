# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    back_date = fields.Date(
        string='Back Date',
        copy=False,
        tracking=True,
        help='Set a back date to override the scheduled date and '
             'effective (done) date of this transfer.',
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
        """Apply back_date to the stock picking and its move lines."""
        for picking in self:
            if not picking.back_date:
                raise UserError(_('Please set a Back Date before applying.'))
            if picking.state == 'cancel':
                raise UserError(_('Cannot apply back date on a cancelled transfer.'))

            back_date = picking.back_date
            back_datetime = fields.Datetime.to_datetime(str(back_date) + ' 00:00:00')

            # Update picking dates
            write_vals = {
                'scheduled_date': back_datetime,
                'back_date_applied': True,
            }
            # If already done, update the effective date too
            if picking.state == 'done':
                write_vals['date_done'] = back_datetime

            picking.write(write_vals)

            # Update stock move dates
            picking.move_ids.write({'date': back_datetime})

            # Update stock move line dates
            picking.move_line_ids.write({'date': back_datetime})

            picking.message_post(
                body=_(
                    'Back Date <b>%s</b> applied. '
                    'Scheduled date and move dates updated.'
                ) % back_date
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Back Date Applied'),
                'message': _('Back date has been applied successfully to Transfer(s).'),
                'type': 'success',
                'sticky': False,
            },
        }

    # ------------------------------------------------------------------ #
    #  Override _action_done to use back_date as effective date          #
    # ------------------------------------------------------------------ #
    def _action_done(self):
        for picking in self:
            if picking.back_date:
                back_datetime = fields.Datetime.to_datetime(
                    str(picking.back_date) + ' 00:00:00'
                )
                picking.move_ids.write({'date': back_datetime})
                picking.move_line_ids.write({'date': back_datetime})
        result = super()._action_done()
        for picking in self:
            if picking.back_date and picking.state == 'done':
                picking.write({
                    'date_done': fields.Datetime.to_datetime(
                        str(picking.back_date) + ' 00:00:00'
                    ),
                    'back_date_applied': True,
                })
        return result
