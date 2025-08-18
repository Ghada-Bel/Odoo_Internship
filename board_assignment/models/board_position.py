from odoo import models, fields

class BoardPosition(models.Model):
    _name = 'board.position'
    _description = 'Board Position'

    title = fields.Char(string="Position Title", required=True)
    organization = fields.Char(string="Organization")
    is_vacant = fields.Boolean(default=True)
    requested_by = fields.Char()
    status = fields.Selection([
        ('requested', 'Requested'),
        ('reviewed', 'Reviewed'),
        ('assigned', 'Assigned')
    ], default='requested')
