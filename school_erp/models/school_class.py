from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolGrade(models.Model):
    """Academic grade / standard (e.g. Grade 10)."""
    _name = 'school.grade'
    _description = 'School Grade'
    _order = 'sequence, name'

    name = fields.Char('Grade Name', required=True, translate=True)
    code = fields.Char('Code', size=10, required=True)
    sequence = fields.Integer('Sequence', default=10)
    class_ids = fields.One2many('school.class', 'grade_id', string='Classes')
    class_count = fields.Integer('Classes', compute='_compute_class_count')
    active = fields.Boolean(default=True)

    @api.depends('class_ids')
    def _compute_class_count(self):
        for rec in self:
            rec.class_count = len(rec.class_ids)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Grade code must be unique.'),
    ]


class SchoolClass(models.Model):
    """A class = one grade + one section (e.g. Grade 10 - Section A)."""
    _name = 'school.class'
    _description = 'School Class'
    _rec_name = 'display_name'
    _order = 'grade_id, section'

    grade_id = fields.Many2one('school.grade', string='Grade', required=True, ondelete='restrict')
    section = fields.Char('Section', size=5, required=True, help="e.g. A, B, C")
    display_name = fields.Char('Class Name', compute='_compute_display_name', store=True)
    academic_year = fields.Char('Academic Year', required=True, default=lambda self: self._default_academic_year())
    class_teacher_id = fields.Many2one('hr.employee', string='Class Teacher')
    room = fields.Char('Classroom / Room No.')
    capacity = fields.Integer('Max Capacity', default=40)

    student_ids = fields.One2many('school.student', 'class_id', string='Students')
    student_count = fields.Integer('Students', compute='_compute_student_count')

    timetable_ids = fields.One2many('school.timetable', 'class_id', string='Timetable')
    active = fields.Boolean(default=True)
    color = fields.Integer('Color Index')

    @staticmethod
    def _default_academic_year():
        from datetime import date
        y = date.today().year
        return f"{y}-{str(y + 1)[2:]}"

    @api.depends('grade_id', 'section', 'academic_year')
    def _compute_display_name(self):
        for rec in self:
            grade = rec.grade_id.name or ''
            rec.display_name = f"{grade} – {rec.section}" if grade else rec.section

    @api.depends('student_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)

    @api.constrains('capacity', 'student_ids')
    def _check_capacity(self):
        for rec in self:
            if rec.capacity and len(rec.student_ids) > rec.capacity:
                raise ValidationError(
                    _('Class %s has exceeded its capacity of %d students.') % (rec.display_name, rec.capacity)
                )

    _sql_constraints = [
        ('class_section_year_uniq', 'unique(grade_id, section, academic_year)',
         'A class with this grade, section and academic year already exists.'),
    ]
