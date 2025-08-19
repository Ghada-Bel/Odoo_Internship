# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class CandidateOnboarding(models.Model):
    _name = 'candidate.onboarding'
    _description = 'Candidate Onboarding'
    _order = 'create_date desc'
    _inherit = ['mail.thread']  # For message_main_attachment_id

    # Basic Information - matching DB schema
    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    template_id = fields.Many2one('onboarding.template', string='Onboarding Template', required=True)
    current_step_id = fields.Many2one('onboarding.step', string='Current Step')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    
    # Many2many for completed steps - using correct relation table name and columns
    completed_step_ids = fields.Many2many('onboarding.step', 
                                          relation='onboarding_completed_steps_rel',
                                          column1='candidate_onboarding_id',
                                          column2='onboarding_step_id',
                                          string='Completed Steps')

    # Personal Information Fields - matching DB columns exactly
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    id_number = fields.Char(string='ID Number')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    birth_date = fields.Date(string='Date of Birth')  # DB has birth_date, not date_of_birth
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], string='Marital Status')
    dependents = fields.Integer(string='Number of Dependents', default=0)  # DB has dependents, not dependencies

    # Additional Information Fields - matching DB schema
    country_id = fields.Many2one('res.country', string='Country')  # DB has country_id
    phone = fields.Char(string='Telephone')
    physical_address = fields.Text(string='Physical Address')
    citizenship = fields.Char(string='Citizenship')
    birthplace = fields.Char(string='Birthplace')
    education_field = fields.Char(string='Education Field')  # DB has education_field
    occupation = fields.Char(string='Occupation')
    next_of_kin = fields.Char(string='Next of Kin')

    # Qualification Fields - matching DB schema
    qualification = fields.Char(string='Highest Qualification')  # DB has qualification
    field_of_study = fields.Char(string='Field of Study')  # DB has field_of_study
    institution = fields.Char(string='School/Institution')
    graduation_year = fields.Integer(string='Graduation Year')  # DB has graduation_year

    # Skills Fields - matching DB schema exactly
    other_technical_skill = fields.Char(string='Technical Skills')
    other_interpersonal_skill = fields.Char(string='Interpersonal Skills')
    other_management_skill = fields.Char(string='Management Skills')
    other_cognitive_skill = fields.Char(string='Cognitive Skills')
    other_personal_attribute = fields.Char(string='Personal Attributes')

    # Availability - matching DB schema
    availability = fields.Char(string='Availability')

    # Documents - matching DB schema
    cv_filename = fields.Char(string='CV Filename')
    cover_letter_filename = fields.Char(string='Cover Letter Filename')

    # Relationships to other tables
    other_qualification_ids = fields.One2many('onboarding.qualification', 'onboarding_id', string='Other Qualifications')
    work_experience_ids = fields.One2many('onboarding.work.experience', 'onboarding_id', string='Work Experience')
    reference_ids = fields.One2many('onboarding.reference', 'onboarding_id', string='References')

    # Computed fields for progress
    progress_percentage = fields.Float(string='Progress (%)', compute='_compute_progress')

    @api.depends('completed_step_ids', 'template_id.step_ids')
    def _compute_progress(self):
        for record in self:
            if record.template_id and record.template_id.step_ids:
                total_steps = len(record.template_id.step_ids)
                completed_steps = len(record.completed_step_ids)
                record.progress_percentage = (completed_steps / total_steps) * 100
            else:
                record.progress_percentage = 0.0

    @api.model
    def create(self, vals):
        onboarding = super(CandidateOnboarding, self).create(vals)
        if onboarding.template_id and onboarding.template_id.step_ids:
            first_step = onboarding.template_id.step_ids.sorted('sequence')[0]
            onboarding.current_step_id = first_step.id
        return onboarding

    def action_next_step(self):
        """Move to the next step in the onboarding process"""
        for record in self:
            if not record.current_step_id:
                continue

            if record.current_step_id.id not in record.completed_step_ids.ids:
                record.completed_step_ids = [(4, record.current_step_id.id)]

            steps = record.template_id.step_ids.sorted('sequence')
            current_index = steps.ids.index(record.current_step_id.id) if record.current_step_id.id in steps.ids else None

            if current_index is not None and current_index < len(steps) - 1:
                record.current_step_id = steps[current_index + 1].id

    def action_prev_step(self):
        """Move to the previous step in the onboarding process"""
        for record in self:
            if not record.current_step_id:
                continue

            steps = record.template_id.step_ids.sorted('sequence')
            current_index = steps.ids.index(record.current_step_id.id) if record.current_step_id.id in steps.ids else None

            if current_index is not None and current_index > 0:
                prev_step = steps[current_index - 1]
                # Remove current step from completed if needed
                if record.current_step_id.id in record.completed_step_ids.ids:
                    record.completed_step_ids = [(3, record.current_step_id.id)]
                record.current_step_id = prev_step.id

    def action_go_to_step(self, step_name):
        """Navigate to a specific step by name"""
        for record in self:
            step = record.template_id.step_ids.filtered(lambda s: s.name == step_name)
            if step:
                record.current_step_id = step[0].id
                return True
        return False

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and not re.match(r'^\+?[\d\s\-\(\)]{8,}$', record.phone):
                raise ValidationError(_('Please enter a valid phone number.'))

    @api.constrains('dependents')
    def _check_dependents(self):
        for record in self:
            if record.dependents and record.dependents < 0:
                raise ValidationError(_('Number of dependents cannot be negative.'))


class OnboardingTemplate(models.Model):
    _name = 'onboarding.template'
    _description = 'Onboarding Template'

    name = fields.Char(string='Template Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    step_ids = fields.One2many('onboarding.step', 'template_id', string='Steps')


class OnboardingStep(models.Model):
    _name = 'onboarding.step'
    _description = 'Onboarding Step'
    _order = 'sequence, id'

    name = fields.Char(string='Step Name', required=True, translate=True)  # jsonb field needs translate=True
    sequence = fields.Integer(string='Sequence', default=10)
    template_id = fields.Many2one('onboarding.template', string='Template', required=True, ondelete='cascade')
    view_id = fields.Many2one('ir.ui.view', string='View')
    is_active = fields.Boolean(string='Active', default=True)
    required = fields.Boolean(string='Required', default=True)


class OnboardingSkill(models.Model):
    _name = 'onboarding.skill'
    _description = 'Onboarding Skill'

    name = fields.Char(string='Skill Name', required=True)
    skill_type = fields.Selection([
        ('technical', 'Technical'),
        ('interpersonal', 'Interpersonal'), 
        ('management', 'Management'),
        ('cognitive', 'Cognitive'),
        ('personal', 'Personal')
    ], string='Skill Type', required=True)


class OnboardingQualification(models.Model):
    _name = 'onboarding.qualification'
    _description = 'Onboarding Additional Qualification'

    onboarding_id = fields.Many2one('candidate.onboarding', required=True, ondelete='cascade')
    qualification = fields.Char(string='Qualification Name', required=True)
    field_of_study = fields.Char(string='Field of Study')
    institution = fields.Char(string='Institution')
    year = fields.Integer(string='Year Completed')


class OnboardingReference(models.Model):
    _name = 'onboarding.reference'
    _description = 'Onboarding Reference'

    onboarding_id = fields.Many2one('candidate.onboarding', required=True, ondelete='cascade')
    name = fields.Char(string='Reference Name', required=True)
    company = fields.Char(string='Company')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')


class OnboardingWorkExperience(models.Model):
    _name = 'onboarding.work.experience'
    _description = 'Onboarding Work Experience'

    onboarding_id = fields.Many2one('candidate.onboarding', required=True, ondelete='cascade')
    company = fields.Char(string='Company Name', required=True)
    position = fields.Char(string='Position')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    currently_working = fields.Boolean(string='Currently Working', default=False)
