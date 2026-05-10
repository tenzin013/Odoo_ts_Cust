import requests
from odoo import models, fields, api
from odoo.exceptions import UserError


class ApiConnector(models.Model):
    _name = 'api.connector'
    _description = 'API Connector'

    name = fields.Char(required=True)
    base_url = fields.Char(required=True)
    api_key = fields.Char(string='API Key')
    auth_type = fields.Selection([
        ('none', 'None'),
        ('api_key', 'API Key'),
        ('bearer', 'Bearer Token')
    ], default='none')

    http_method = fields.Selection([
        ('get', 'GET'),
        ('post', 'POST')
    ], default='get')

    target_model_id = fields.Many2one(
        'ir.model',
        string='Target Odoo Model',
        required=True
    )

    field_mapping_ids = fields.One2many(
        'api.field.mapping',
        'connector_id',
        string='Field Mappings'
    )

    active = fields.Boolean(default=True)

    def action_test_connection(self):
        for rec in self:
            headers = {}
            if rec.auth_type == 'api_key':
                headers['x-api-key'] = rec.api_key
            elif rec.auth_type == 'bearer':
                headers['Authorization'] = f'Bearer {rec.api_key}'

            try:
                response = requests.get(rec.base_url, headers=headers, timeout=10)
                if response.status_code in [200, 201]:
                    raise UserError("Connection Successful!")
                else:
                    raise UserError(f"Connection Failed! Status: {response.status_code}")
            except Exception as e:
                raise UserError(str(e))

    def action_import_data(self):
        for rec in self:
            headers = {}
            if rec.auth_type == 'api_key':
                headers['x-api-key'] = rec.api_key
            elif rec.auth_type == 'bearer':
                headers['Authorization'] = f'Bearer {rec.api_key}'

            response = requests.get(rec.base_url, headers=headers, timeout=20)

            if response.status_code != 200:
                raise UserError("Failed to fetch API data.")

            data = response.json()

            if isinstance(data, dict):
                data = [data]

            model_name = rec.target_model_id.model
            model = self.env[model_name]

            for item in data:
                vals = {}

                for mapping in rec.field_mapping_ids:
                    api_field = mapping.api_field
                    odoo_field = mapping.odoo_field

                    vals[odoo_field] = item.get(api_field)

                model.create(vals)
