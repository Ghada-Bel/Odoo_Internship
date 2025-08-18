# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CandidateOnboarding(models.Model):
    _name = 'candidate.onboarding'
    _description = 'Candidate Onboarding'
    _order = 'create_date desc'

    # Basic Information
    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    template_id = fields.Many2one('onboarding.template', string='Onboarding Template', required=True)
    current_step_id = fields.Many2one('onboarding.step', string='Current Step')
    completed_step_ids = fields.Many2many('onboarding.step', string='Completed Steps')
    
    # Personal Information Fields
    first_name = fields.Char(string='First Name', required=True)
    surname = fields.Char(string='Surname', required=True)
    id_number = fields.Char(string='ID Number', required=True)
    email = fields.Char(string='Email Address', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', required=True)
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], string='Marital Status', required=True)
    dependencies = fields.Integer(string='Number of Dependencies', default=0)
    
    # Additional Information Fields
    country = fields.Many2one('res.country', string='Country')
    phone = fields.Char(string='Telephone')
    physical_address = fields.Text(string='Physical Address')
    citizenship = fields.Char(string='Citizenship')
    birthplace = fields.Char(string='Birthplace')
    field_id = fields.Many2one('onboarding.field', string='Field')
    occupation = fields.Char(string='Occupation')
    next_of_kin = fields.Char(string='Next of Kin')
    
    # Qualification Fields
    qualification_level = fields.Selection([
        ('matric', 'Matric'),
        ('diploma', 'Diploma'),
        ('degree', 'Degree'),
        ('masters', "Master's"),
        ('phd', 'PhD')
    ], string='Highest Qualification')
    qualification_field = fields.Char(string='Qualification Field/Subject')
    institution = fields.Char(string='School/Institution')
    qualification_year = fields.Integer(string='Year Completed')
    
    # Other qualifications
    other_qualification_ids = fields.One2many('onboarding.qualification', 'onboarding_id', string='Other Qualifications')
    
    # Work Experience
    work_experience_ids = fields.One2many('onboarding.work.experience', 'onboarding_id', string='Work Experience')
    
    # Skills
    skill_ids = fields.One2many('onboarding.skill.assignment', 'onboarding_id', string='Skills')
    
    # Availability
    start_date = fields.Date(string='Available Start Date')
    notice_period = fields.Integer(string='Notice Period (days)')
    
    # References
    reference_ids = fields.One2many('onboarding.reference', 'onboarding_id', string='References')
    
    # Documents
    cv = fields.Binary(string='CV/Resume', attachment=True)
    cv_filename = fields.Char(string='CV Filename')
    cover_letter = fields.Binary(string='Cover Letter', attachment=True)
    cover_letter_filename = fields.Char(string='Cover Letter Filename')
    id_document = fields.Binary(string='ID Document', attachment=True)
    id_document_filename = fields.Char(string='ID Document Filename')
    certificates = fields.Binary(string='Certificates', attachment=True)
    certificates_filename = fields.Char(string='Certificates Filename')
    
    # Status fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft')
    
    completion_date = fields.Datetime(string='Completion Date')
    progress_percentage = fields.Float(string='Progress (%)', compute='_compute_progress')

    @api.depends('completed_step_ids', 'template_id.step_ids')
    def _compute_progress(self):
        for record in self:
            if record.template_id.step_ids:
                total_steps = len(record.template_id.step_ids)
                completed_steps = len(record.completed_step_ids)
                record.progress_percentage = (completed_steps / total_steps) * 100
            else:
                record.progress_percentage = 0.0

    @api.model
    def create(self, vals):
        # Set initial step when creating onboarding
        onboarding = super(CandidateOnboarding, self).create(vals)
        if onboarding.template_id and onboarding.template_id.step_ids:
            first_step = onboarding.template_id.step_ids.sorted('sequence')[0]
            onboarding.current_step_id = first_step.id
            onboarding.state = 'in_progress'
        return onboarding

    def action_next_step(self):
        """Move to the next step in the onboarding process"""
        if not self.current_step_id:
            return
            
        # Mark current step as completed
        if self.current_step_id.id not in self.completed_step_ids.ids:
            self.completed_step_ids = [(4, self.current_step_id.id)]
        
        # Find next step
        steps = self.template_id.step_ids.sorted('sequence')
        current_index = None
        for i, step in enumerate(steps):
            if step.id == self.current_step_id.id:
                current_index = i
                break
        
        if current_index is not None and current_index < len(steps) - 1:
            # Move to next step
            next_step = steps[current_index + 1]
            self.current_step_id = next_step.id
        else:
            # This was the last step - mark as completed
            self.state = 'completed'
            self.completion_date = fields.Datetime.now()
            self.current_step_id = False

    def action_prev_step(self):
        """Move to the previous step in the onboarding process"""
        if not self.current_step_id:
            return
            
        steps = self.template_id.step_ids.sorted('sequence')
        current_index = None
        for i, step in enumerate(steps):
            if step.id == self.current_step_id.id:
                current_index = i
                break
        
        if current_index is not None and current_index > 0:
            # Move to previous step
            prev_step = steps[current_index - 1]
            self.current_step_id = prev_step.id
            # Remove current step from completed if it was completed
            if self.current_step_id.id in self.completed_step_ids.ids:
                self.completed_step_ids = [(3, self.current_step_id.id)]

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                import re
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', record.email):
                    raise ValidationError(_('Please enter a valid email address.'))

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone:
                import re
                if not re.match(r'^\+?[\d\s\-\(\)]{8,}$', record.phone):
                    raise ValidationError(_('Please enter a valid phone number.'))

    @api.constrains('dependencies')
    def _check_dependencies(self):
        for record in self:
            if record.dependencies < 0:
                raise ValidationError(_('Number of dependencies cannot be negative.'))


class OnboardingTemplate(models.Model):
    _name = 'onboarding.template'
    _description = 'Onboarding Template'

    name = fields.Char(string='Template Name', required=True)
    description = fields.Text(string='Description')
    step_ids = fields.One2many('onboarding.step', 'template_id', string='Steps')
    active = fields.Boolean(string='Active', default=True)


class OnboardingStep(models.Model):
    _name = 'onboarding.step'
    _description = 'Onboarding Step'
    _order = 'sequence, id'

    name = fields.Char(string='Step Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    template_id = fields.Many2one('onboarding.template', string='Template', required=True, ondelete='cascade')
    description = fields.Text(string='Description')
    required = fields.Boolean(string='Required', default=True)
    active = fields.Boolean(string='Active', default=True)


class OnboardingField(models.Model):
    _name = 'onboarding.field'
    _description = 'Onboarding Field/Sector'

    name = fields.Char(string='Field Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)


class OnboardingSkillAssignment(models.Model):
    _name = 'onboarding.skill.assignment'
    _description = 'Skill Assignment to Onboarding'
    
    onboarding_id = fields.Many2one('candidate.onboarding', required=True, ondelete='cascade')
    skill_id = fields.Many2one('onboarding.skill', required=True)
    skill_type = fields.Selection(related='skill_id.skill_type', store=True)
