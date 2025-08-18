from odoo import models, fields

class OnboardingReference(models.Model):
    _name = 'onboarding.reference'
    _description = 'Candidate Reference'

    onboarding_id = fields.Many2one('candidate.onboarding')
    name = fields.Char(required=True)
    company = fields.Char(string="Company/Organization", required=True)
    phone = fields.Char(required=True)
    email = fields.Char()
