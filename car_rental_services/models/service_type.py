# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CarRentalServiceType(models.Model):
    _name = 'car.rental.service.type'
    _description = 'Car Rental Service Type'
    _order = 'sequence, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ── Core Fields ──────────────────────────────────────────
    name = fields.Char(
        string='Service Type Name',
        required=True,
        tracking=True,
        help="Name of the rental service type (e.g., Economy, Luxury, SUV)"
    )
    code = fields.Char(
        string='Code',
        size=10,
        tracking=True,
        help="Short unique code for the service type (e.g., ECO, LUX, SUV)"
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Determines the display order of service types"
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help="Inactive service types are hidden from views"
    )
    color = fields.Integer(
        string='Color Index',
        default=0
    )

    # ── Category & Classification ────────────────────────────
    category = fields.Selection([
        ('economy', 'Economy'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('luxury', 'Luxury'),
        ('suv', 'SUV / 4x4'),
        ('van', 'Van / Minibus'),
        ('electric', 'Electric / Hybrid'),
        ('chauffeur', 'Chauffeur Driven'),
        ('special', 'Special / Classic'),
    ], string='Category', required=True, default='standard', tracking=True)

    vehicle_class = fields.Selection([
        ('a', 'Class A – Mini'),
        ('b', 'Class B – Economy'),
        ('c', 'Class C – Compact'),
        ('d', 'Class D – Mid-size'),
        ('e', 'Class E – Full-size'),
        ('f', 'Class F – Premium'),
        ('g', 'Class G – SUV'),
        ('h', 'Class H – Van'),
        ('i', 'Class I – Luxury'),
        ('j', 'Class J – Sports'),
    ], string='Vehicle Class', default='c')

    # ── Pricing ───────────────────────────────────────────────
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    base_daily_rate = fields.Monetary(
        string='Base Daily Rate',
        currency_field='currency_id',
        tracking=True,
        help="Standard daily rental rate for this service type"
    )
    weekend_rate = fields.Monetary(
        string='Weekend Daily Rate',
        currency_field='currency_id',
        help="Rate applied on weekends (Saturday & Sunday)"
    )
    weekly_rate = fields.Monetary(
        string='Weekly Rate',
        currency_field='currency_id',
        help="Flat rate for a 7-day rental"
    )
    monthly_rate = fields.Monetary(
        string='Monthly Rate',
        currency_field='currency_id',
        help="Flat rate for a 30-day rental"
    )
    security_deposit = fields.Monetary(
        string='Security Deposit',
        currency_field='currency_id',
        help="Refundable deposit collected at booking"
    )

    # ── Inclusions & Features ─────────────────────────────────
    description = fields.Html(
        string='Description',
        help="Detailed description of the service type shown to customers"
    )
    includes_driver = fields.Boolean(
        string='Includes Driver',
        default=False,
        help="Tick if a chauffeur/driver is included in this service"
    )
    includes_fuel = fields.Boolean(
        string='Includes Fuel',
        default=False,
        help="Tick if fuel costs are covered in the rate"
    )
    includes_insurance = fields.Boolean(
        string='Includes Insurance',
        default=True,
        help="Tick if basic insurance is bundled"
    )
    includes_gps = fields.Boolean(
        string='Includes GPS',
        default=False
    )
    includes_child_seat = fields.Boolean(
        string='Child Seat Available',
        default=False
    )
    max_passengers = fields.Integer(
        string='Max Passengers',
        default=5,
        help="Maximum number of passengers for vehicles in this category"
    )
    min_rental_days = fields.Integer(
        string='Minimum Rental Days',
        default=1
    )
    free_km_per_day = fields.Integer(
        string='Free KM per Day',
        default=200,
        help="Kilometres included in the daily rate before extra charges apply"
    )
    extra_km_charge = fields.Monetary(
        string='Extra KM Charge',
        currency_field='currency_id',
        help="Charge per extra kilometre beyond the free allowance"
    )

    # ── Related Records ───────────────────────────────────────
    vehicle_ids = fields.One2many(
        'car.rental.vehicle',
        'service_type_id',
        string='Vehicles'
    )
    vehicle_count = fields.Integer(
        string='Vehicle Count',
        compute='_compute_vehicle_count',
        store=True
    )
    booking_ids = fields.One2many(
        'car.rental.booking',
        'service_type_id',
        string='Bookings'
    )
    booking_count = fields.Integer(
        string='Booking Count',
        compute='_compute_booking_count',
        store=True
    )

    # ── Status ────────────────────────────────────────────────
    image = fields.Image(
        string='Service Image',
        max_width=1024,
        max_height=1024
    )
    notes = fields.Text(
        string='Internal Notes'
    )

    # ── Computed Fields ───────────────────────────────────────
    @api.depends('vehicle_ids')
    def _compute_vehicle_count(self):
        for rec in self:
            rec.vehicle_count = len(rec.vehicle_ids)

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for rec in self:
            rec.booking_count = len(rec.booking_ids)

    # ── Constraints ───────────────────────────────────────────
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Service Type name must be unique!'),
        ('code_uniq', 'unique(code)', 'Service Type code must be unique!'),
    ]

    @api.constrains('base_daily_rate', 'min_rental_days', 'max_passengers')
    def _check_positive_values(self):
        for rec in self:
            if rec.base_daily_rate < 0:
                raise ValidationError(_("Base daily rate cannot be negative."))
            if rec.min_rental_days < 1:
                raise ValidationError(_("Minimum rental days must be at least 1."))
            if rec.max_passengers < 1:
                raise ValidationError(_("Maximum passengers must be at least 1."))

    # ── Actions ───────────────────────────────────────────────
    def action_view_vehicles(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vehicles – %s') % self.name,
            'res_model': 'car.rental.vehicle',
            'view_mode': 'list,form',
            'domain': [('service_type_id', '=', self.id)],
            'context': {'default_service_type_id': self.id},
        }

    def action_view_bookings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bookings – %s') % self.name,
            'res_model': 'car.rental.booking',
            'view_mode': 'list,form',
            'domain': [('service_type_id', '=', self.id)],
            'context': {'default_service_type_id': self.id},
        }

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active

    # ── Name get ─────────────────────────────────────────────
    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.code:
                name = f'[{rec.code}] {name}'
            result.append((rec.id, name))
        return result
