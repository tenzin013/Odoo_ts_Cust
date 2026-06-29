# -*- coding: utf-8 -*-
import base64
import json
import logging

from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class FaceAttendanceController(http.Controller):

    # ── Face Encodings (serve stored descriptors to JS kiosk) ────────────────

    @http.route(
        '/hr_attendance_face/get_encodings',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
    )
    def get_face_encodings(self):
        """Return all employee face descriptors for client-side matching."""
        try:
            encodings = request.env['hr.employee'].sudo().get_all_face_encodings()
            return {'status': 'ok', 'employees': encodings}
        except Exception as e:
            _logger.exception('get_face_encodings error')
            return {'status': 'error', 'message': str(e)}

    # ── Enrolment (store face-api.js descriptor from browser) ─────────────────

    @http.route(
        '/hr_attendance_face/enroll_descriptor',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def enroll_descriptor(self, employee_id, face_image, descriptor):
        """
        Store the 128-d face descriptor (computed by face-api.js in the browser)
        and the reference face image for the given employee.
        """
        if not descriptor or len(descriptor) != 128:
            return {'status': 'error', 'message': 'Invalid descriptor — expected 128 floats.'}

        try:
            employee = request.env['hr.employee'].sudo().browse(int(employee_id))
        except (ValueError, TypeError):
            return {'status': 'error', 'message': 'Invalid employee_id.'}

        if not employee.exists():
            return {'status': 'error', 'message': 'Employee not found.'}

        try:
            employee.write({
                'face_image':         face_image,
                'face_encoding':      json.dumps(descriptor),
                'face_encoding_date': fields.Datetime.now(),
            })
        except Exception as e:
            _logger.exception('enroll_descriptor write error for employee %s', employee_id)
            return {'status': 'error', 'message': str(e)}

        _logger.info('Face descriptor enrolled for employee %s (id=%s)', employee.name, employee_id)
        return {'status': 'ok', 'message': 'Descriptor saved.'}

    # ── Kiosk Check-in/Out ────────────────────────────────────────────────────

    @http.route(
        '/hr_attendance_face/kiosk/checkin',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
    )
    def kiosk_checkin(self, employee_id=None, latitude=None, longitude=None):
        """
        Record attendance for an employee already identified client-side.
        Performs geofence validation (if enabled) then writes hr.attendance.
        """
        # Validate employee_id up front — bad value here causes a traceback
        # that Odoo wraps in an HTML error page, breaking the JSON parse.
        if not employee_id:
            return {'status': 'error', 'message': 'employee_id is required.'}

        try:
            employee_id = int(employee_id)
        except (ValueError, TypeError):
            return {'status': 'error', 'message': 'Invalid employee_id.'}

        try:
            ICP = request.env['ir.config_parameter'].sudo()
            geofencing = ICP.get_param(
                'hr_attendance_face_detection.face_attendance_geofencing', False
            )

            # ── Geofence check ────────────────────────────────────────────────
            matched_location = None
            if geofencing:
                if not latitude or not longitude:
                    return {
                        'status': 'error',
                        'message': 'GPS location required. Please allow location access.',
                    }
                location, dist = request.env['face.attendance.location'].sudo().find_matching_location(
                    float(latitude), float(longitude)
                )
                if not location:
                    return {
                        'status': 'error',
                        'message': (
                            'You are not within any allowed attendance location. '
                            'Move closer to a registered site and try again.'
                        ),
                    }
                matched_location = location

            # ── Fetch employee ────────────────────────────────────────────────
            employee = request.env['hr.employee'].sudo().browse(employee_id)
            if not employee.exists():
                return {'status': 'error', 'message': 'Employee not found.'}
            if not employee.face_recognition_enabled:
                return {'status': 'error', 'message': 'Face recognition is disabled for this employee.'}

            # ── Record attendance ─────────────────────────────────────────────
            return self._process_attendance(employee, latitude, longitude, matched_location)

        except Exception as e:
            _logger.exception('kiosk_checkin error for employee_id=%s', employee_id)
            return {'status': 'error', 'message': 'Server error: ' + str(e)}

    # ── Attendance processing ─────────────────────────────────────────────────

    def _process_attendance(self, employee, latitude, longitude, location):
        Attendance = request.env['hr.attendance'].sudo()
        now        = fields.Datetime.now()

        open_att = Attendance.search([
            ('employee_id', '=', employee.id),
            ('check_out',   '=', False),
        ], limit=1)

        if open_att:
            vals = {
                'check_out':               now,
                'check_out_face_verified':  True,
                'attendance_mode':          'face',
            }
            if latitude:
                vals['check_out_latitude']  = float(latitude)
                vals['check_out_longitude'] = float(longitude)
            if location:
                vals['check_out_location_id'] = location.id
            open_att.write(vals)
            action = 'check_out'
        else:
            vals = {
                'employee_id':             employee.id,
                'check_in':                now,
                'check_in_face_verified':  True,
                'attendance_mode':         'face',
            }
            if latitude:
                vals['check_in_latitude']  = float(latitude)
                vals['check_in_longitude'] = float(longitude)
            if location:
                vals['check_in_location_id'] = location.id
            Attendance.create(vals)
            action = 'check_in'

        employee.write({'last_face_check': now})

        return {
            'status':        'ok',
            'employee_id':   employee.id,
            'employee_name': employee.name,
            'action':        action,
            'timestamp':     fields.Datetime.to_string(now),
            'location':      location.name if location else '',
        }

    # ── Location Test ─────────────────────────────────────────────────────────

    @http.route(
        '/hr_attendance_face/test_location',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def test_location(self, latitude, longitude):
        try:
            location, dist = request.env['face.attendance.location'].sudo().find_matching_location(
                float(latitude), float(longitude)
            )
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

        if location:
            return {
                'status':   'ok',
                'location': location.name,
                'distance': dist,
                'radius':   location.radius_meters,
            }
        return {'status': 'outside', 'message': 'Not within any configured attendance location.'}
