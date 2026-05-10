# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CarRentalVehicle(models.Model):
    _name = 'car.rental.vehicle'
    _description = 'Car Rental Vehicle'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ── Identification ────────────────────────────────────────
    name = fields.Char(
        string='Vehicle Name / Model',
        required=True,
        tracking=True,
        help="e.g., Toyota Camry 2023"
    )
    license_plate = fields.Char(
        string='License Plate',
        required=True,
        tracking=True
    )
    vin = fields.Char(
        string='VIN / Chassis No.',
        tracking=True
    )
    image = fields.Image(
        string='Vehicle Photo',
        max_width=1024,
        max_height=1024
    )

    # ── Classification ────────────────────────────────────────
    service_type_id = fields.Many2one(
        'car.rental.service.type',
        string='Service Type',
        required=True,
        tracking=True,
        ondelete='restrict'
    )
    brand = fields.Char(string='Brand / Make', tracking=True)
    model_year = fields.Integer(string='Year', default=2024)
    color = fields.Char(string='Color')
    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
        ('lpg', 'LPG'),
    ], string='Fuel Type', default='petrol')
    transmission = fields.Selection([
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('cvt', 'CVT'),
    ], string='Transmission', default='automatic')
    seats = fields.Integer(string='Seats', default=5)

    # ── Status ────────────────────────────────────────────────
    state = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'In Maintenance'),
        ('reserved', 'Reserved'),
        ('inactive', 'Inactive'),
    ], string='Status', default='available', tracking=True)
    active = fields.Boolean(default=True)

    # ── Odometer & Maintenance ────────────────────────────────
    odometer = fields.Float(string='Current Odometer (km)', digits=(10, 2))
    last_service_date = fields.Date(string='Last Service Date')
    next_service_km = fields.Float(string='Next Service at (km)')
    insurance_expiry = fields.Date(string='Insurance Expiry')
    registration_expiry = fields.Date(string='Registration Expiry')

    # ── Financials ────────────────────────────────────────────
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    purchase_value = fields.Monetary(
        string='Purchase Value',
        currency_field='currency_id'
    )
    daily_rate_override = fields.Monetary(
        string='Daily Rate Override',
        currency_field='currency_id',
        help="Leave 0 to use the service type rate"
    )

    # ── Bookings ──────────────────────────────────────────────
    booking_ids = fields.One2many(
        'car.rental.booking',
        'vehicle_id',
        string='Bookings'
    )
    booking_count = fields.Integer(
        compute='_compute_booking_count',
        string='Bookings'
    )

    notes = fields.Text(string='Notes')

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for rec in self:
            rec.booking_count = len(rec.booking_ids)

    _sql_constraints = [
        ('plate_uniq', 'unique(license_plate)', 'License plate must be unique!'),
    ]

    def action_set_available(self):
        self.write({'state': 'available'})

    def action_set_maintenance(self):
        self.write({'state': 'maintenance'})

    def action_view_bookings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bookings – %s') % self.name,
            'res_model': 'car.rental.booking',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
        }
