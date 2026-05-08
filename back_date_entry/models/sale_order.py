# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    back_date = fields.Date(
        string='Back Date',
        copy=False,
        tracking=True,
        help='Set a back date to override the order confirmation date, '
             'invoice dates and all linked delivery dates.',
    )
    back_date_applied = fields.Boolean(
        string='Back Date Applied',
        copy=False,
        default=False,
        readonly=True,
    )

    # ------------------------------------------------------------------ #
    #  Onchange — live preview while editing                              #
    # ------------------------------------------------------------------ #
    @api.onchange('back_date')
    def _onchange_back_date(self):
        if self.back_date and self.back_date > fields.Date.today():
            return {
                'warning': {
                    'title': _('Future Date Warning'),
                    'message': _(
                        'The back date you entered (%s) is in the future. '
                        'Back dates are normally in the past.'
                    ) % self.back_date,
                }
            }

    # ------------------------------------------------------------------ #
    #  Public method — apply the back date                               #
    # ------------------------------------------------------------------ #
    def action_apply_back_date(self):
        """Apply back_date to the sale order and all its linked records."""
        for order in self:
            if not order.back_date:
                raise UserError(_('Please set a Back Date before applying.'))

            back_date = order.back_date
            back_datetime = fields.Datetime.to_datetime(str(back_date) + ' 00:00:00')

            # 1. Sale Order dates
            write_vals = {
                'date_order': back_datetime,
                'back_date_applied': True,
            }
            # commitment_date available on confirmed orders
            if order.commitment_date:
                write_vals['commitment_date'] = back_datetime

            order.write(write_vals)

            # 2. Linked stock pickings (deliveries)
            for picking in order.picking_ids.filtered(
                lambda p: p.state not in ('done', 'cancel')
            ):
                picking.write({
                    'scheduled_date': back_datetime,
                    'back_date': back_date,
                })

            # 3. Linked invoices / account moves
            for inv in order.invoice_ids.filtered(
                lambda m: m.state == 'draft'
            ):
                inv.write({
                    'invoice_date': back_date,
                    'date': back_date,
                    'back_date': back_date,
                })

            order.message_post(
                body=_(
                    'Back Date <b>%s</b> applied. '
                    'Order date, delivery dates and draft invoice dates updated.'
                ) % back_date
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Back Date Applied'),
                'message': _('Back date has been applied successfully to Sale Order(s).'),
                'type': 'success',
                'sticky': False,
            },
        }
