# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class OnboardingStep(models.Model):
    _name = 'onboarding.step'
    _description = 'Configurable Onboarding Step'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    is_active = fields.Boolean(default=True)
    template_id = fields.Many2one('onboarding.template')
    # IMPORTANT: QWeb templates, not backend form views
    view_id = fields.Many2one(
        'ir.ui.view',
        domain="[('type', '=', 'qweb')]",
        help="QWeb template to render for this step (website/portal fragment)."
    )
    required = fields.Boolean(default=True, help="Is this step mandatory?")

class OnboardingTemplate(models.Model):
    _name = 'onboarding.template'
    _description = 'Onboarding Process Template'

    name = fields.Char(required=True)
    step_ids = fields.One2many('onboarding.step', 'template_id', string="Steps")
    active = fields.Boolean(default=True)

class CandidateOnboarding(models.Model):
    _name = 'candidate.onboarding'
    _description = 'Candidate Onboarding Process'
    _inherit = ['mail.thread']

    # Basic Information
    user_id = fields.Many2one('res.users', required=True, index=True)
    template_id = fields.Many2one('onboarding.template', required=True, domain="[('active', '=', True)]")
    current_step_id = fields.Many2one('onboarding.step', compute='_compute_current_step', store=True)
    completed_step_ids = fields.Many2many('onboarding.step', relation='onboarding_completed_steps_rel')

    # ========== Step 1: Personal Information ==========
    first_name = fields.Char()
    last_name = fields.Char()
    id_number = fields.Char(string="National ID")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    birth_date = fields.Date(string="Date of Birth")
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married')
    ])
    dependents = fields.Integer(string="Number of Dependents")

    # ========== Step 2: Additional Information ==========
    country_id = fields.Many2one('res.country', string="Country")
    phone = fields.Char()
    physical_address = fields.Text(string="Address")
    citizenship = fields.Char()
    birthplace = fields.Char()
    education_field = fields.Selection([
        ('computer_science', 'Computer Science'),
        ('engineering', 'Engineering'),
        ('business', 'Business'),
        ('healthcare', 'Healthcare'),
        ('other', 'Other')
    ], string="Field of Education/Training")
    occupation = fields.Selection([
        ('developer', 'Developer'),
        ('manager', 'Manager'),
        ('analyst', 'Analyst'),
        ('other', 'Other')
    ])
    next_of_kin = fields.Char(string="Next of Kin")

    # ========== Step 3: Highest Qualification ==========
    qualification = fields.Selection([
        ('phd', 'PhD'),
        ('master', "Master's Degree"),
        ('bachelor', "Bachelor's Degree"),
        ('diploma', 'Diploma'),
        ('certificate', 'Certificate')
    ], string="Highest Qualification")
    field_of_study = fields.Char(string="Field of Study")
    institution = fields.Char(string="Institution")
    graduation_year = fields.Integer(string="Year of Graduation")

    # ========== Step 4: Other Qualifications ==========
    other_qualification_ids = fields.One2many('onboarding.qualification', 'onboarding_id', string="Other Qualifications")

    # ========== Step 5: Work Experience ==========
    work_experience_ids = fields.One2many('onboarding.work.experience', 'onboarding_id', string="Work Experiences")

    # ========== Step 6: Skills ==========
    technical_skill_ids = fields.Many2many('onboarding.skill', relation='onboarding_technical_skill_rel', string="Technical Skills")
    other_technical_skill = fields.Char(string="Other Technical Skills")

    interpersonal_skill_ids = fields.Many2many('onboarding.skill', relation='onboarding_interpersonal_skill_rel', string="Interpersonal Skills")
    other_interpersonal_skill = fields.Char(string="Other Interpersonal Skills")

    management_skill_ids = fields.Many2many('onboarding.skill', relation='onboarding_management_skill_rel', string="Management Skills")
    other_management_skill = fields.Char(string="Other Management Skills")

    cognitive_skill_ids = fields.Many2many('onboarding.skill', relation='onboarding_cognitive_skill_rel', string="Cognitive Skills")
    other_cognitive_skill = fields.Char(string="Other Cognitive Skills")

    personal_attribute_ids = fields.Many2many('onboarding.skill', relation='onboarding_personal_attribute_rel', string="Personal Attributes")
    other_personal_attribute = fields.Char(string="Other Personal Attributes")

    # ========== Step 7: Availability ==========
    availability = fields.Selection([
        ('immediate', 'Immediately'),
        ('1_month', 'Within 1 Month'),
        ('3_months', 'Within 3 Months'),
        ('negotiable', 'Negotiable')
    ], string="Availability")

    # ========== Step 8: References ==========
    reference_ids = fields.One2many('onboarding.reference', 'onboarding_id', string="References")

    # ========== Step 9: Documents ==========
    cover_letter = fields.Binary(string="Cover Letter (PDF)")
    cover_letter_filename = fields.Char(string="Cover Letter Filename")
    cv = fields.Binary(string="CV (PDF)")
    cv_filename = fields.Char(string="CV Filename")

    # HR Integration
    employee_id = fields.Many2one('hr.employee', string="Employee Record")

    @api.constrains('cv_filename', 'cover_letter_filename')
    def _check_pdf_files(self):
        for rec in self:
            for fname in [rec.cv_filename, rec.cover_letter_filename]:
                if fname and not fname.lower().endswith('.pdf'):
                    raise ValidationError("Only PDF files are allowed for CV and Cover Letter.")

    @api.depends('template_id')
    def _compute_current_step(self):
        for rec in self:
            steps = rec.template_id.step_ids.sorted('sequence')
            rec.current_step_id = steps[0] if steps else False

    def action_next_step(self):
        self.ensure_one()
        steps = self.template_id.step_ids.sorted('sequence')
        current_index = steps.ids.index(self.current_step_id.id)
        if current_index + 1 < len(steps):
            self.write({
                'current_step_id': steps[current_index + 1].id,
                'completed_step_ids': [(4, self.current_step_id.id)]
            })
        else:
            self._create_hr_employee()

    def action_prev_step(self):
        self.ensure_one()
        steps = self.template_id.step_ids.sorted('sequence')
        current_index = steps.ids.index(self.current_step_id.id)
        if current_index > 0:
            self.write({
                'current_step_id': steps[current_index - 1].id,
                'completed_step_ids': [(3, self.current_step_id.id)]
            })

    def _create_hr_employee(self):
        """Create HR employee record from onboarding data"""
        self.ensure_one()
        if not self.employee_id:
            employee = self.env['hr.employee'].sudo().create({
                'name': f"{self.first_name or ''} {self.last_name or ''}".strip(),
                'work_email': self.user_id.email,
                'private_phone': self.phone,
                'identification_id': self.id_number,
                'gender': self.gender,
                'birthday': self.birth_date,
                'marital': self.marital_status,
                'onboarding_id': self.id,
            })
            self.employee_id = employee.id
        return self.employee_id


# ---- Extend hr.employee with backlink ----
class HREmployee(models.Model):
    _inherit = 'hr.employee'
    onboarding_id = fields.Many2one('candidate.onboarding', string="Candidate Onboarding")
