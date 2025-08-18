from odoo import models, fields

class OnboardingSkill(models.Model):
    _name = 'onboarding.skill'
    _description = 'Candidate Skill'

    name = fields.Char(required=True)
    skill_type = fields.Selection([
        ('technical', 'Technical'),
        ('interpersonal', 'Interpersonal'),
        ('management', 'Management'),
        ('cognitive', 'Cognitive'),
        ('personal', 'Personal Attribute')
    ], required=True)
