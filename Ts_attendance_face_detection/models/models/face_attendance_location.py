# -*- coding: utf-8 -*-
import math
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class FaceAttendanceLocation(models.Model):
    _name = 'face.attendance.location'
    _description = 'Face Attendance Location'
    _order = 'name'

    name = fields.Char(string='Location Name', required=True)
    active = fields.Boolean(default=True)

    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        required=True,
        help='GPS latitude of the allowed attendance location.',
    )
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        required=True,
        help='GPS longitude of the allowed attendance location.',
    )
    radius_meters = fields.Integer(
        string='Allowed Radius (m)',
        default=100,
        required=True,
        help='Employees must be within this many metres to mark attendance.',
    )
    address = fields.Char(string='Address / Description')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    employee_count = fields.Integer(
        string='Check-ins (today)',
        compute='_compute_employee_count',
    )

    # ── Constraints ───────────────────────────────────────────────────────────

    @api.constrains('latitude')
    def _check_latitude(self):
        for rec in self:
            if not (-90 <= rec.latitude <= 90):
                raise ValidationError(_('Latitude must be between -90 and 90.'))

    @api.constrains('longitude')
    def _check_longitude(self):
        for rec in self:
            if not (-180 <= rec.longitude <= 180):
                raise ValidationError(_('Longitude must be between -180 and 180.'))

    @api.constrains('radius_meters')
    def _check_radius(self):
        for rec in self:
            if rec.radius_meters < 10:
                raise ValidationError(_('Radius must be at least 10 metres.'))

    # ── Compute ───────────────────────────────────────────────────────────────

    def _compute_employee_count(self):
        today = fields.Date.today()
        for rec in self:
            rec.employee_count = self.env['hr.attendance'].search_count([
                ('check_in_location_id', '=', rec.id),
                ('check_in', '>=', str(today) + ' 00:00:00'),
            ])

    # ── Business Logic ────────────────────────────────────────────────────────

    def is_within_radius(self, lat, lng):
        """Haversine distance check. Returns True if (lat, lng) is within radius."""
        self.ensure_one()
        R = 6371000  # Earth radius in metres
        phi1 = math.radians(self.latitude)
        phi2 = math.radians(lat)
        dphi = math.radians(lat - self.latitude)
        dlambda = math.radians(lng - self.longitude)

        a = (math.sin(dphi / 2) ** 2
             + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance <= self.radius_meters, round(distance, 1)

    @api.model
    def find_matching_location(self, lat, lng):
        """
        Return the first active location whose geofence contains (lat, lng).
        Returns (location_record | None, distance_metres).
        """
        locations = self.search([('active', '=', True)])
        for loc in locations:
            within, dist = loc.is_within_radius(lat, lng)
            if within:
                return loc, dist
        return None, None

    # ── Map action ────────────────────────────────────────────────────────────

    def action_open_map(self):
        self.ensure_one()
        url = (
            'https://www.openstreetmap.org/?mlat=%s&mlon=%s#map=16/%s/%s'
            % (self.latitude, self.longitude, self.latitude, self.longitude)
        )
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
