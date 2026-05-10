# -*- coding: utf-8 -*-
{
    'name': 'Car Rental Services',
    'version': '19.0.1.0.0',
    'category': 'Industries',
    'summary': 'Manage Car Rental Services with Service Types, Fleet, and Bookings',
    'description': """
Car Rental Services Module for Odoo 19
========================================

A comprehensive Car Rental Management solution that allows you to:

* **Service Types Management** – Define and categorize your rental service offerings
  (Standard, Luxury, Economy, SUV, Chauffeur, Airport Transfer, etc.)
* **Fleet Management** – Track vehicles, availability, mileage, and condition
* **Booking Management** – Handle customer reservations with pricing and scheduling
* **Customer Management** – Maintain customer profiles and rental history
* **Pricing Rules** – Set base rates, daily rates, and additional charges per service type
* **Dashboard & Reporting** – Get real-time insights on fleet utilization and revenue

Perfect for car rental agencies, corporate fleets, and vehicle leasing businesses.
    """,
    'author': 'Car Rental Solutions',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'product',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/service_type_data.xml',
        'views/service_type_views.xml',
        'views/car_rental_vehicle_views.xml',
        'views/car_rental_booking_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {},
}
