from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime


class SchoolIDCard(models.Model):
    """
    Student ID Card record.
    Tracks generation, printing and validity of each card.
    """
    _name = 'school.idcard'
    _description = 'Student ID Card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'card_number'
    _order = 'issue_date desc'

    # ── Core fields ───────────────────────────────────────────────────────────
    card_number = fields.Char('Card Number', required=True, copy=False,
                              default='/', readonly=True)
    student_id = fields.Many2one('school.student', string='Student', required=True,
                                 ondelete='cascade', index=True, tracking=True)
    academic_year = fields.Char('Academic Year', required=True)

    # Related / display
    student_name = fields.Char(related='student_id.name', store=True)
    class_id = fields.Many2one(related='student_id.class_id', store=True)
    roll_number = fields.Char(related='student_id.roll_number', store=True)
    photo = fields.Binary(related='student_id.photo')
    blood_group = fields.Selection(related='student_id.blood_group', store=True)
    date_of_birth = fields.Date(related='student_id.date_of_birth', store=True)
    period_group_id = fields.Many2one(related='student_id.period_group_id', store=True)

    # ── Dates ─────────────────────────────────────────────────────────────────
    issue_date = fields.Date('Issue Date', default=fields.Date.today, tracking=True)
    valid_till = fields.Date('Valid Till', compute='_compute_valid_till', store=True)

    # ── Status ────────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('pending', 'Pending Print'),
        ('printed', 'Printed'),
        ('active', 'Active / Issued'),
        ('lost', 'Reported Lost'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', tracking=True, required=True)

    print_date = fields.Date('Print Date', tracking=True)
    printed_by = fields.Many2one('res.users', string='Printed By', readonly=True)
    issue_count = fields.Integer('Issue Count', default=1, help="Incremented on re-issue")

    barcode = fields.Char('Barcode', compute='_compute_barcode', store=True)
    notes = fields.Text('Notes')

    # ── Computed ──────────────────────────────────────────────────────────────
    @api.depends('issue_date')
    def _compute_valid_till(self):
        for rec in self:
            if rec.issue_date:
                # Valid for one full academic year (approximately 12 months)
                rec.valid_till = rec.issue_date.replace(
                    year=rec.issue_date.year + 1
                )
            else:
                rec.valid_till = False

    @api.depends('card_number', 'student_id.roll_number')
    def _compute_barcode(self):
        for rec in self:
            roll = rec.student_id.roll_number or 'NA'
            rec.barcode = f"ERP-{roll}-{rec.academic_year.replace('-', '')}".upper()

    # ── Constraints ───────────────────────────────────────────────────────────
    _sql_constraints = [
        ('card_number_uniq', 'unique(card_number)', 'Card number must be unique.'),
    ]

    # ── Workflow actions ──────────────────────────────────────────────────────
    def action_mark_printed(self):
        for rec in self:
            if rec.state != 'pending':
                raise UserError(_('Only cards in "Pending Print" status can be marked as printed.'))
            rec.write({
                'state': 'printed',
                'print_date': fields.Date.today(),
                'printed_by': self.env.uid,
            })

    def action_issue(self):
        for rec in self:
            if rec.state not in ('pending', 'printed'):
                raise UserError(_('Card must be printed before issuing.'))
            rec.write({'state': 'active'})

    def action_report_lost(self):
        self.write({'state': 'lost'})

    def action_reissue(self):
        """Cancel current card and create a replacement."""
        for rec in self:
            rec.write({'state': 'cancelled'})
            self.create({
                'student_id': rec.student_id.id,
                'academic_year': rec.academic_year,
                'issue_count': rec.issue_count + 1,
                'notes': f'Re-issued. Previous card: {rec.card_number}',
            })

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_print_report(self):
        return self.env.ref('school_erp.action_report_student_idcard').report_action(
            self.mapped('student_id')
        )

    # ── ORM ───────────────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('card_number', '/') == '/':
                vals['card_number'] = self.env['ir.sequence'].next_by_code('school.idcard') or '/'
        return super().create(vals_list)
