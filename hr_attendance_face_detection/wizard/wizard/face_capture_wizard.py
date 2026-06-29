# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FaceCaptureWizard(models.TransientModel):
    _name = 'face.capture.wizard'
    _description = 'Face Capture Wizard'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.context.get('active_id'),
    )
    captured_image = fields.Binary(string='Captured Image', required=True)
    captured_image_filename = fields.Char(default='face_capture.jpg')

    def action_save_and_encode(self):
        self.ensure_one()
        if not self.captured_image:
            raise UserError(_('No image captured. Please use the webcam to capture your face.'))

        self.employee_id.write({
            'face_image': self.captured_image,
            'face_image_filename': self.captured_image_filename,
        })
        self.employee_id.action_generate_face_encoding()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Face Enrolled'),
                'message': _('Face image captured and encoding generated for %s.') % self.employee_id.name,
                'type': 'success',
            },
        }
