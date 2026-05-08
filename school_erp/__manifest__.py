{
    'name': 'School ERP — Class, Period & ID Card Management',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Manage students, classes, periods, timetables and ID cards',
    'description': """
School ERP Module for Odoo 19
==============================
Features:
- Student registration linked to res.partner
- Class & section management
- Period and subject configuration
- Weekly timetable builder
- Student ID card generation and print management
- Batch ID card printing with QR/barcode
    """,
    'author': 'EduERP',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'contacts',
        'web',
    ],
    'author': 'Tshering Sherpa',
    'website': 'https://www.linkedin.com/in/tshering-sherpa-a17184278/',
    'maintainer': 'Tshering Sherpa',
    'support': 'tsherings8981@gmail.com',
    'price':'10.00',
    'currency':'USD',
    'data': [
        'security/school_security.xml',
        'security/ir.model.access.csv',
        'data/school_data.xml',
        'views/school_student_views.xml',
        'views/school_class_views.xml',
        'views/school_period_views.xml',
        'views/school_timetable_views.xml',
        'views/school_idcard_views.xml',
        'views/school_menus.xml',
        'report/school_idcard_report.xml',
        'report/school_idcard_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'school_erp/static/src/css/school_erp.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
