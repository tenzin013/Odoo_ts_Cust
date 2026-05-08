# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    back_date = fields.Date(
        string='Back Date',
        copy=False,
        tracking=True,
        help='Set a back date to override the purchase order date, '
             'vendor bill dates and all linked receipt dates.',
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
                        'The back date (%s) is in the future. '
                        'Back dates are normally in the past.'
                    ) % self.back_date,
                }
            }

    def action_apply_back_date(self):
        """Apply back_date to the purchase order and all its linked records."""
        for order in self:
            if not order.back_date:
                raise UserError(_('Please set a Back Date before applying.'))

            back_date = order.back_date
            back_datetime = fields.Datetime.to_datetime(str(back_date) + ' 00:00:00')

            # 1. Purchase Order date
            order.write({
                'date_order': back_datetime,
                'date_approve': back_datetime,
                'back_date_applied': True,
            })

            # 2. Linked stock pickings (receipts)
            for picking in order.picking_ids.filtered(
                lambda p: p.state not in ('done', 'cancel')
            ):
                picking.write({
                    'scheduled_date': back_datetime,
                    'back_date': back_date,
                })

            # 3. Linked vendor bills / account moves (draft only)
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
                    'Order date, receipt dates and draft bill dates updated.'
                ) % back_date
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Back Date Applied'),
                'message': _('Back date has been applied successfully to Purchase Order(s).'),
                'type': 'success',
                'sticky': False,
            },
        }
