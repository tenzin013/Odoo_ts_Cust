from odoo import fields, models


class SchoolSubject(models.Model):
    """Academic subject (e.g. Mathematics, Physics)."""
    _name = 'school.subject'
    _description = 'School Subject'
    _order = 'name'

    name = fields.Char('Subject Name', required=True, translate=True)
    code = fields.Char('Subject Code', size=10, required=True)
    subject_type = fields.Selection([
        ('core', 'Core / Compulsory'),
        ('elective', 'Elective'),
        ('activity', 'Activity / Co-curricular'),
        ('language', 'Language'),
    ], string='Type', default='core', required=True)
    color = fields.Char('Display Color', default='#714B67', help="Hex color used in timetable display")
    description = fields.Text('Description')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Subject code must be unique.'),
    ]
