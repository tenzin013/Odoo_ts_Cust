# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class FaceAttendanceKioskController(http.Controller):

    @http.route(
        '/hr_attendance_face/kiosk',
        type='http',
        auth='public',
        website=False,
        csrf=False,
    )
    def kiosk(self, **kwargs):
        """Render the full-screen kiosk attendance page."""
        ICP = request.env['ir.config_parameter'].sudo()
        kiosk_enabled = ICP.get_param(
            'hr_attendance_face_detection.face_attendance_kiosk_mode', True
        )
        if not kiosk_enabled:
            return request.not_found()

        # Safely resolve company_id — get_param always returns a string or False
        company = None
        try:
            company_id_raw = ICP.get_param('web.company_id', False)
            if company_id_raw:
                company = request.env['res.company'].sudo().browse(int(company_id_raw))
                if not company.exists():
                    company = None
        except (ValueError, TypeError):
            company = None

        if not company:
            company = request.env['res.company'].sudo().search([], limit=1)

        geofencing = ICP.get_param(
            'hr_attendance_face_detection.face_attendance_geofencing', False
        )

        return request.render(
            'hr_attendance_face_detection.kiosk_page',
            {
                'company':    company,
                'geofencing': geofencing,
            },
        )
