# -*- coding: utf-8 -*-
{
    'name': 'HR Attendance Face Detection',
    'version': '18.0.2.0.1',
    'category': 'Human Resources/Attendances',
    'summary': 'Face Recognition Attendance with GPS Geofencing for Odoo 18 Community',
    'description': """
HR Attendance Face Detection
=============================
Contactless, AI-driven attendance solution using client-side facial recognition.

Features:
---------
* Face Recognition Check-In / Check-Out via webcam (client-side, no Python ML)
* Uses face-api.js (TinyFaceDetector) — runs entirely in the browser
* GPS Geofencing — restrict attendance to defined locations & radius
* Multi-location support
* Kiosk Mode for shared terminals
* Employee face enrolment from employee profile (descriptor stored server-side)
* Attendance logs
* Real-time face detection feedback
* Works with standard webcams — no extra hardware needed
* Fully integrated with Odoo 18 Community HR Attendance module

Installation Requirements:
--------------------------
No extra Python packages required.
Requires internet access on the kiosk browser to load face-api.js from CDN.

    """,
    'author': 'Tshering Sherpa',
    'website': '',
    'license': 'LGPL-3',
    'price': 20.00,
    'currency': 'USD',
    'depends': [
        'hr_attendance',
        'hr',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/res_config_settings_views.xml',
        'views/face_attendance_location_views.xml',
        'views/kiosk_templates.xml',
        'views/menu_items.xml',
        'data/ir_cron_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Backend: enrollment widget CSS + JS only
            'hr_attendance_face_detection/static/src/css/face_detection.css',
            'hr_attendance_face_detection/static/src/js/face_enrollment.js',
        ],
        # NOTE: kiosk.css and face_api_kiosk.js are NOT bundled here.
        # They are loaded directly by the standalone kiosk template (kiosk_templates.xml)
        # via plain <link> and <script> tags, since the kiosk page is auth='public'
        # and does not load any Odoo asset bundles.
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
