from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class SchoolStudent(models.Model):
    """
    School student record.
    Linked to res.partner for contact data.
    """
    _name = 'school.student'
    _description = 'School Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'class_id, roll_number'

    # ── Identity ────────────────────────────────────────────────────────────
    name = fields.Char('Full Name', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Contact', ondelete='restrict',
                                 help="Linked Odoo contact record")
    photo = fields.Binary('Photo', attachment=True)
    photo_filename = fields.Char()

    gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other')
    ], string='Gender', tracking=True)
    date_of_birth = fields.Date('Date of Birth')
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A−'), ('B+', 'B+'), ('B-', 'B−'),
        ('AB+', 'AB+'), ('AB-', 'AB−'), ('O+', 'O+'), ('O-', 'O−'),
    ], string='Blood Group')
    nationality_id = fields.Many2one('res.country', string='Nationality')

    # ── Admission ────────────────────────────────────────────────────────────
    admission_number = fields.Char('Admission No.', required=True, copy=False, tracking=True)
    admission_date = fields.Date('Admission Date', default=fields.Date.today)
    academic_year = fields.Char('Academic Year', required=True,
                                default=lambda self: self._default_academic_year())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('transferred', 'Transferred'),
        ('alumni', 'Alumni'),
    ], string='Status', default='draft', tracking=True, required=True)

    # ── Class & Period ────────────────────────────────────────────────────────
    class_id = fields.Many2one('school.class', string='Class', tracking=True, ondelete='restrict')
    roll_number = fields.Char('Roll Number', size=20, tracking=True)
    period_group_id = fields.Many2one('school.period.group', string='Period Group',
                                      help="Determines which daily period schedule applies")

    # ── Guardian ─────────────────────────────────────────────────────────────
    guardian_name = fields.Char('Guardian Name')
    guardian_relation = fields.Selection([
        ('father', 'Father'), ('mother', 'Mother'),
        ('guardian', 'Legal Guardian'), ('other', 'Other'),
    ], string='Relation')
    guardian_phone = fields.Char('Guardian Phone')
    guardian_email = fields.Char('Guardian Email')

    # ── Address ──────────────────────────────────────────────────────────────
    street = fields.Char('Street')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char('ZIP')
    country_id = fields.Many2one('res.country', string='Country')

    # ── ID Card ───────────────────────────────────────────────────────────────
    idcard_ids = fields.One2many('school.idcard', 'student_id', string='ID Cards')
    idcard_count = fields.Integer('ID Cards', compute='_compute_idcard_count')
    active_idcard_id = fields.Many2one('school.idcard', string='Active ID Card',
                                       compute='_compute_active_idcard')

    active = fields.Boolean(default=True)
    notes = fields.Text('Internal Notes')

    # ── Computed ──────────────────────────────────────────────────────────────
    age = fields.Integer('Age', compute='_compute_age')

    @staticmethod
    def _default_academic_year():
        from datetime import date
        y = date.today().year
        return f"{y}-{str(y + 1)[2:]}"

    @api.depends('date_of_birth')
    def _compute_age(self):
        from datetime import date
        today = date.today()
        for rec in self:
            if rec.date_of_birth:
                dob = rec.date_of_birth
                rec.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                rec.age = 0

    @api.depends('idcard_ids')
    def _compute_idcard_count(self):
        for rec in self:
            rec.idcard_count = len(rec.idcard_ids)

    @api.depends('idcard_ids', 'idcard_ids.state')
    def _compute_active_idcard(self):
        for rec in self:
            active = rec.idcard_ids.filtered(lambda c: c.state == 'active')
            rec.active_idcard_id = active[:1]

    # ── Constraints ───────────────────────────────────────────────────────────
    _sql_constraints = [
        ('admission_number_uniq', 'unique(admission_number)',
         'Admission number must be unique.'),
        ('class_roll_uniq', 'unique(class_id, roll_number)',
         'Roll number must be unique within a class.'),
    ]

    @api.constrains('guardian_email')
    def _check_guardian_email(self):
        pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        for rec in self:
            if rec.guardian_email and not re.match(pattern, rec.guardian_email):
                raise ValidationError(_('Invalid guardian email address.'))

    # ── Actions ───────────────────────────────────────────────────────────────
    def action_activate(self):
        self.write({'state': 'active'})

    def action_set_leave(self):
        self.write({'state': 'on_leave'})

    def action_transfer(self):
        self.write({'state': 'transferred'})

    def action_generate_idcard(self):
        """Create a new pending ID card for each selected student."""
        IDCard = self.env['school.idcard']
        for student in self:
            # Expire existing active cards
            student.idcard_ids.filtered(lambda c: c.state == 'active').write({'state': 'expired'})
            IDCard.create({
                'student_id': student.id,
                'academic_year': student.academic_year,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': _('ID Cards'),
            'res_model': 'school.idcard',
            'view_mode': 'list,form',
            'domain': [('student_id', 'in', self.ids)],
        }

    def action_view_idcards(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('ID Cards'),
            'res_model': 'school.idcard',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
        }

    def action_print_idcard(self):
        return self.env.ref('school_erp.action_report_student_idcard').report_action(self)

    # ── ORM overrides ─────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('admission_number'):
                vals['admission_number'] = self.env['ir.sequence'].next_by_code('school.student') or '/'
        return super().create(vals_list)
