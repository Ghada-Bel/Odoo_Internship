from odoo import models, fields

class OnboardingSkillAssignment(models.Model):
    _name = 'onboarding.skill.assignment'
    _description = 'Skill Assignment to Onboarding'
    
    onboarding_id = fields.Many2one('candidate.onboarding', required=True, ondelete='cascade')
    skill_id = fields.Many2one('onboarding.skill', required=True)
    skill_type = fields.Selection(related='skill_id.skill_type', store=True)
