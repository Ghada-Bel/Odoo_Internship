from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import random
import string

class EmailVerification(models.Model):
    _name = 'candidate_portal.verification'
    _description = 'Email Verification'

    email = fields.Char(required=True)
    code = fields.Char(string='Verification Code', required=True)
    expiration = fields.Datetime(string='Expires At')

    def send_verification_email(self):
        for record in self:
            if not record.email:
                raise UserError("Email address is required.")

            mail_values = {
                'subject': 'Your Verification Code',
                'body_html': f"""
                    <p>Hello,</p>
                    <p>Your verification code is <strong>{record.code}</strong>.</p>
                    <p>This code expires in 10 minutes.</p>
                """,
                'email_to': record.email,
                'email_from': self.env.user.email or 'noreply@example.com',
            }

            self.env['mail.mail'].create(mail_values).send()
