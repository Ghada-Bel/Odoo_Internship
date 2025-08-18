from odoo import models, fields

class OnboardingWorkExperience(models.Model):
    _name = 'onboarding.work.experience'
    _description = 'Candidate Work Experience'

    onboarding_id = fields.Many2one('candidate.onboarding')
    company = fields.Char(string="Company/Organization", required=True)
    position = fields.Char(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    currently_working = fields.Boolean(string="Currently Working Here")
