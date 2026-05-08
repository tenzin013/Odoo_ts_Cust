from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


DAY_SELECTION = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
]


class SchoolTimetable(models.Model):
    """
    Weekly timetable entry.
    One record = one class × one day × one period × one subject + teacher.
    """
    _name = 'school.timetable'
    _description = 'School Timetable Entry'
    _order = 'class_id, day_of_week, period_id'

    class_id = fields.Many2one('school.class', string='Class', required=True, ondelete='cascade', index=True)
    academic_year = fields.Char('Academic Year', related='class_id.academic_year', store=True)
    day_of_week = fields.Selection(DAY_SELECTION, string='Day', required=True)
    period_id = fields.Many2one('school.period', string='Period', required=True, ondelete='restrict')
    subject_id = fields.Many2one('school.subject', string='Subject', ondelete='restrict')
    teacher_id = fields.Many2one('hr.employee', string='Teacher')
    room = fields.Char('Room / Lab')
    notes = fields.Char('Notes')

    period_type = fields.Selection(related='period_id.period_type', store=True)
    time_start_display = fields.Char(related='period_id.time_start_display')
    time_end_display = fields.Char(related='period_id.time_end_display')

    _sql_constraints = [
        ('class_day_period_uniq', 'unique(class_id, day_of_week, period_id)',
         'A timetable entry already exists for this class, day and period.'),
    ]

    @api.constrains('period_type', 'subject_id')
    def _check_subject_required(self):
        for rec in self:
            if rec.period_type == 'regular' and not rec.subject_id:
                raise ValidationError(
                    _('Subject is required for regular period "%s".') % rec.period_id.name
                )

    def name_get(self):
        result = []
        day_map = dict(DAY_SELECTION)
        for rec in self:
            day = day_map.get(rec.day_of_week, '')
            subj = rec.subject_id.name if rec.subject_id else rec.period_id.name
            result.append((rec.id, f"{rec.class_id.display_name} | {day} | {subj}"))
        return result
