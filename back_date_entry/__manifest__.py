# -*- coding: utf-8 -*-
{
    'name': 'Back Date Entry',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Allow back-dated entries across Sales, Purchase, Accounting and Stock Transfers',
    'description': """
Back Date Entry for Odoo 18
============================
This module allows users to apply a back date across:
- Sales Orders (Confirmation Date & Delivery Date)
- Purchase Orders (Order Date & Receipt Date)
- Journal Entries / Accounting Moves (Accounting Date)
- Stock Transfers / Pickings (Scheduled & Effective Date)

When a back date is set on any of these records, all related
dates are automatically updated to reflect that back date,
ensuring accurate reporting and compliance.

Features
--------
* Back Date field on Sale Order, Purchase Order, Account Move and Stock Picking
* Automatic propagation to linked pickings, invoices and journal entries
* Dedicated Back Date wizard for bulk/batch updates
* Access rights controlled — only Managers can apply back dates
* Full audit trail preserved via chatter log
    """,
    'author': 'Tshering Sherpa',
    'website': 'https://www.linkedin.com/in/tshering-sherpa-a17184278/',
    'maintainer': 'Tshering Sherpa',
    'support': 'tsherings8981@gmail.com',
    'price':'10.00',
    'currency':'USD',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'purchase',
        'account',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/back_date_wizard_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
