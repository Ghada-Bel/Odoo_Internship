from odoo import models, fields

class BoardMember(models.Model):
    _name = 'board.member'
    _description = 'Board Member'

    name = fields.Char(string="Full Name", required=True)
    email = fields.Char()
    phone = fields.Char()
    assigned_position_id = fields.Many2one('board.position', string="Assigned Position")
    term_start = fields.Date()
    term_end = fields.Date()
    state = fields.Selection([
        ('active', 'Active'),
        ('ended', 'Term Ended')
    ], default='active')
