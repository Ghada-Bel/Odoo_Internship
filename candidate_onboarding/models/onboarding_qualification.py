from odoo import models, fields

class OnboardingQualification(models.Model):
    _name = 'onboarding.qualification'
    _description = 'Candidate Additional Qualification'

    onboarding_id = fields.Many2one('candidate.onboarding')
    qualification = fields.Selection([
        ('phd', 'PhD'),
        ('master', 'Master\'s Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('diploma', 'Diploma'),
        ('certificate', 'Certificate')
    ], required=True)
    field_of_study = fields.Char(required=True)
    institution = fields.Char(required=True)
    year = fields.Integer(string="Year of Completion", required=True)
