# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    # ── Face / GPS extras ────────────────────────────────────────────────────

    check_in_face_image = fields.Binary(
        string='Check-In Snapshot',
        attachment=True,
        help='Snapshot captured at check-in for audit purposes.',
    )
    check_out_face_image = fields.Binary(
        string='Check-Out Snapshot',
        attachment=True,
        help='Snapshot captured at check-out for audit purposes.',
    )
    check_in_face_verified = fields.Boolean(
        string='Check-In Face Verified',
        default=False,
    )
    check_out_face_verified = fields.Boolean(
        string='Check-Out Face Verified',
        default=False,
    )

    check_in_latitude = fields.Float(string='Check-In Latitude', digits=(10, 7))
    check_in_longitude = fields.Float(string='Check-In Longitude', digits=(10, 7))
    check_out_latitude = fields.Float(string='Check-Out Latitude', digits=(10, 7))
    check_out_longitude = fields.Float(string='Check-Out Longitude', digits=(10, 7))

    check_in_location_id = fields.Many2one(
        'face.attendance.location',
        string='Check-In Location',
    )
    check_out_location_id = fields.Many2one(
        'face.attendance.location',
        string='Check-Out Location',
    )

    attendance_mode = fields.Selection([
        ('face', 'Face Recognition'),
        ('manual', 'Manual'),
        ('kiosk', 'Kiosk'),
    ], string='Attendance Mode', default='manual')

    # ── Cron method — no imports needed, all odoo framework available ─────────

    @api.model
    def _cron_auto_checkout(self):
        """Called by ir.cron — close open attendances from previous days."""
        ICP = self.env['ir.config_parameter'].sudo()
        if not ICP.get_param('hr_attendance_face_detection.face_attendance_auto_checkout'):
            return

        now = fields.Datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

        open_atts = self.sudo().search([('check_out', '=', False)])
        count = 0
        for att in open_atts:
            if att.check_in.date() < now.date():
                att.write({'check_out': midnight})
                count += 1

        if count:
            _logger.info(
                'Face Attendance Auto Check-Out: closed %d open attendance(s).', count
            )
