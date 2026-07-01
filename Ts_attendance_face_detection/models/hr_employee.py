# -*- coding: utf-8 -*-
import json
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # ── Face Recognition Fields ──────────────────────────────────────────────

    face_image = fields.Binary(
        string='Face Image',
        attachment=True,
        help='Reference face image. Captured via webcam during enrolment.',
    )
    face_image_filename = fields.Char(string='Face Image Filename')

    face_encoding = fields.Text(
        string='Face Descriptor',
        help='JSON list of 128 floats — computed by face-api.js in the browser.',
        readonly=True,
    )
    face_encoding_date = fields.Datetime(
        string='Descriptor Generated On',
        readonly=True,
    )
    face_recognition_enabled = fields.Boolean(
        string='Enable Face Recognition',
        default=True,
        help='Allow this employee to check in/out via facial recognition.',
    )
    last_face_check = fields.Datetime(
        string='Last Face Check',
        readonly=True,
    )

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_clear_face_encoding(self):
        """Remove stored face descriptor and image."""
        self.ensure_one()
        self.write({
            'face_encoding':      False,
            'face_encoding_date': False,
            'face_image':         False,
        })
        return {
            'type': 'ir.actions.client',
            'tag':  'display_notification',
            'params': {
                'title':   _('Encoding Cleared'),
                'message': _('Face descriptor for %s has been removed.') % self.name,
                'type':    'warning',
                'sticky':  False,
            },
        }

    # ── Helper: serve descriptors to kiosk ────────────────────────────────────

    @api.model
    def get_all_face_encodings(self):
        """
        Return employee face descriptors for client-side matching in the kiosk.
        Each entry: {id, name, encoding: [128 floats], job_title, department}
        """
        employees = self.search([
            ('face_encoding',           '!=', False),
            ('face_recognition_enabled', '=', True),
            ('active',                   '=', True),
        ])
        result = []
        for emp in employees:
            try:
                enc = json.loads(emp.face_encoding)
                if len(enc) != 128:
                    _logger.warning('Skipping %s — descriptor length %d (expected 128)', emp.name, len(enc))
                    continue
                result.append({
                    'id':         emp.id,
                    'name':       emp.name,
                    'encoding':   enc,
                    'job_title':  emp.job_title or '',
                    'department': emp.department_id.name if emp.department_id else '',
                })
            except Exception:
                _logger.warning('Invalid face descriptor for employee %s', emp.name)
        return result
