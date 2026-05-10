{
        'name': 'API Connector & Field Mapper',
        'version': '19.0.1.0.0',
        'summary': 'Connect Odoo with external APIs and map fields dynamically.',
        'description': '''
API Connector & Field Mapper
============================
Features:
- Configure external APIs
- Store API credentials
- Test API connections
- Dynamic field mapping
- Import data into Odoo models
- Scheduled synchronization support
        ''',
        'category': 'Tools',
        'author': 'Tshering Sherpa',
    'website': 'https://www.linkedin.com/in/tshering-sherpa-a17184278/',
    'maintainer': 'Tshering Sherpa',
    'license': 'LGPL-3',
    'price':'31.13',
    'currency':'USD',
        'depends': ['base'],
        'data': [
            'security/ir.model.access.csv',
            'views/api_connector_views.xml',
            'views/field_mapping_views.xml',
            'views/menu_views.xml',
                
        ],
        'images': [
        'static/description/banner.png'],
        'installable': True,
        'application': True,
    }
