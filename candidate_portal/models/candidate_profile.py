from odoo import models, fields

class CandidateProfile(models.Model):
    _name = 'candidate.profile'
    _description = 'Candidate Profile'

    user_id = fields.Many2one('res.users', string='User Account', required=True)
    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    phone = fields.Char()
    address = fields.Char()
    education = fields.Text()
    motivation_letter = fields.Text()
    cv = fields.Binary(string='CV')
    cv_filename = fields.Char(string='CV Filename')
