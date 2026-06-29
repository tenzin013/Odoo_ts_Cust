# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    face_attendance_enabled = fields.Boolean(
        string='Enable Face Recognition Attendance',
        config_parameter='hr_attendance_face_detection.face_attendance_enabled',
    )
    face_attendance_geofencing = fields.Boolean(
        string='Require GPS Geofencing',
        config_parameter='hr_attendance_face_detection.face_attendance_geofencing',
        help='Employees must be within a configured location radius to check in/out.',
    )
    face_attendance_save_snapshot = fields.Boolean(
        string='Save Face Snapshots',
        config_parameter='hr_attendance_face_detection.face_attendance_save_snapshot',
        default=True,
        help='Store webcam snapshots with each attendance record for audit purposes.',
    )
    face_attendance_threshold = fields.Float(
        string='Recognition Tolerance',
        config_parameter='hr_attendance_face_detection.face_attendance_threshold',
        default=0.55,
        help='Lower = stricter matching (0.4 – 0.65 recommended). Default: 0.55',
    )
    face_attendance_kiosk_mode = fields.Boolean(
        string='Allow Kiosk Mode',
        config_parameter='hr_attendance_face_detection.face_attendance_kiosk_mode',
        default=True,
    )
    face_attendance_auto_checkout = fields.Boolean(
        string='Auto Check-Out at Midnight',
        config_parameter='hr_attendance_face_detection.face_attendance_auto_checkout',
        help='Automatically close open attendances at midnight.',
    )
