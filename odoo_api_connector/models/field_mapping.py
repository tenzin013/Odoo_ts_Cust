from odoo import models, fields


class ApiFieldMapping(models.Model):
    _name = 'api.field.mapping'
    _description = 'API Field Mapping'

    connector_id = fields.Many2one(
        'api.connector',
        required=True,
        ondelete='cascade'
    )

    api_field = fields.Char(required=True)
    odoo_field = fields.Char(required=True)
