# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class CarRentalBooking(models.Model):
    _name = 'car.rental.booking'
    _description = 'Car Rental Booking'
    _order = 'date_from desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference'

    reference = fields.Char(
        string='Booking Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    service_type_id = fields.Many2one('car.rental.service.type', string='Service Type', required=True, tracking=True)
    vehicle_id = fields.Many2one('car.rental.vehicle', string='Vehicle', tracking=True,
        domain="[('service_type_id','=',service_type_id),('state','in',['available','reserved'])]")

    date_from = fields.Datetime(string='Pick-up Date', required=True, tracking=True)
    date_to = fields.Datetime(string='Return Date', required=True, tracking=True)
    rental_days = fields.Integer(string='Rental Days', compute='_compute_rental_days', store=True)

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    daily_rate = fields.Monetary(string='Daily Rate', currency_field='currency_id')
    total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id', compute='_compute_total', store=True)
    security_deposit = fields.Monetary(string='Security Deposit', currency_field='currency_id')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    pickup_location = fields.Char(string='Pick-up Location')
    return_location = fields.Char(string='Return Location')
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('car.rental.booking') or _('New')
        return super().create(vals_list)

    @api.depends('date_from', 'date_to')
    def _compute_rental_days(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                delta = rec.date_to - rec.date_from
                rec.rental_days = max(1, delta.days)
            else:
                rec.rental_days = 0

    @api.depends('daily_rate', 'rental_days')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = rec.daily_rate * rec.rental_days

    @api.onchange('service_type_id')
    def _onchange_service_type(self):
        if self.service_type_id:
            self.daily_rate = self.service_type_id.base_daily_rate
            self.security_deposit = self.service_type_id.security_deposit

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to <= rec.date_from:
                raise ValidationError(_("Return date must be after pick-up date."))

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        if self.vehicle_id:
            self.vehicle_id.state = 'reserved'

    def action_start(self):
        self.write({'state': 'ongoing'})
        if self.vehicle_id:
            self.vehicle_id.state = 'rented'

    def action_return(self):
        self.write({'state': 'returned'})
        if self.vehicle_id:
            self.vehicle_id.state = 'available'

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        if self.vehicle_id and self.vehicle_id.state in ('reserved', 'rented'):
            self.vehicle_id.state = 'available'

    def action_draft(self):
        self.write({'state': 'draft'})
