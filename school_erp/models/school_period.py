from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime


class SchoolPeriodGroup(models.Model):
    """A period group defines a daily schedule template (e.g. Group A, Group B)."""
    _name = 'school.period.group'
    _description = 'Period Group'
    _order = 'name'

    name = fields.Char('Group Name', required=True)
    code = fields.Char('Code', size=10)
    description = fields.Text('Description')
    period_ids = fields.One2many('school.period', 'group_id', string='Periods')
    period_count = fields.Integer('Periods', compute='_compute_period_count')
    active = fields.Boolean(default=True)

    @api.depends('period_ids')
    def _compute_period_count(self):
        for rec in self:
            rec.period_count = len(rec.period_ids)


class SchoolPeriod(models.Model):
    """
    A period is one time slot in a school day.
    Periods are assigned to timetable entries.
    """
    _name = 'school.period'
    _description = 'School Period'
    _order = 'sequence, time_start'

    name = fields.Char('Period Name', required=True, translate=True,
                       help="e.g. Period 1, Lunch Break")
    sequence = fields.Integer('Sequence', default=10)
    group_id = fields.Many2one('school.period.group', string='Period Group', required=True, ondelete='restrict')
    period_type = fields.Selection([
        ('regular', 'Regular Period'),
        ('break', 'Short Break'),
        ('lunch', 'Lunch Break'),
        ('assembly', 'Assembly'),
        ('activity', 'Activity Period'),
    ], string='Type', default='regular', required=True)

    time_start = fields.Float('Start Time', required=True,
                              help="Use 24-hr decimal: 8.5 = 08:30")
    time_end = fields.Float('End Time', required=True)
    duration = fields.Integer('Duration (min)', compute='_compute_duration', store=True)

    time_start_display = fields.Char('Start', compute='_compute_time_display')
    time_end_display = fields.Char('End', compute='_compute_time_display')

    active = fields.Boolean(default=True)

    @api.depends('time_start', 'time_end')
    def _compute_duration(self):
        for rec in self:
            rec.duration = int((rec.time_end - rec.time_start) * 60) if rec.time_end > rec.time_start else 0

    @api.depends('time_start', 'time_end')
    def _compute_time_display(self):
        def fmt(f):
            h = int(f)
            m = int(round((f - h) * 60))
            return f"{h:02d}:{m:02d}"
        for rec in self:
            rec.time_start_display = fmt(rec.time_start)
            rec.time_end_display = fmt(rec.time_end)

    @api.constrains('time_start', 'time_end')
    def _check_times(self):
        for rec in self:
            if rec.time_end <= rec.time_start:
                raise ValidationError(_('End time must be after start time for period "%s".') % rec.name)

    def name_get(self):
        return [(rec.id, f"{rec.name} ({rec.time_start_display}–{rec.time_end_display})") for rec in self]
