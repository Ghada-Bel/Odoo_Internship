from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import random
import string


class CandidateSignup(http.Controller):

    @http.route('/candidate/signup', type='http', auth='public', website=True)
    def signup_form(self, **kw):
        return request.render('candidate_portal.signup_template')

    @http.route('/candidate/signup/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def signup_submit(self, **post):
        first_name = post.get('first_name')
        last_name = post.get('last_name')
        email = post.get('email')
        phone = post.get('phone')
        password = post.get('password')

        # 1. Create user
        user = request.env['res.users'].sudo().create({
            'name': f"{first_name} {last_name}",
            'login': email,
            'email': email,
            'phone': phone,
            'password': password,
            'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
        })

        # 2. Create candidate profile
        request.env['candidate.profile'].sudo().create({
            'user_id': user.id,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
        })

        # 3. Generate verification code
        code = ''.join(random.choices(string.digits, k=6))
        expiration_time = datetime.now() + timedelta(minutes=10)

        # Clean up expired codes
        request.env['candidate_portal.verification'].sudo().search([
            ('expiration', '<', datetime.now())
        ]).unlink()

        # Create or update the verification record
        existing = request.env['candidate_portal.verification'].sudo().search([
            ('email', '=', email)
        ], limit=1)

        if existing:
            existing.write({
                'code': code,
                'expiration': expiration_time,
            })
        else:
            request.env['candidate_portal.verification'].sudo().create({
                'email': email,
                'code': code,
                'expiration': expiration_time,
            })

        # 4. Send email manually using mail.mail
        mail_values = {
            'subject': 'Your Verification Code',
            'body_html': f"""
                <p>Hello {first_name},</p>
                <p>Your verification code is <strong>{code}</strong>.</p>
                <p>This code expires in 10 minutes.</p>
            """,
            'email_to': email,
            'email_from': request.env.user.email or 'noreply@example.com',
        }

        mail = request.env['mail.mail'].sudo().create(mail_values)
        mail.send()

        # 5. Show verification input page
        return request.render('candidate_portal.verify_template', {
            'email': email,
        })

    @http.route('/candidate/verify', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def verify_code(self, **post):
        input_code = post.get('code')
        email = post.get('email')

        record = request.env['candidate_portal.verification'].sudo().search([
            ('email', '=', email),
        ], limit=1)

        if record and record.code == input_code and record.expiration > datetime.now():
            record.unlink()
            return request.redirect("/web/login?verified=1")  
        else:
            return request.render('candidate_portal.verify_template', {
                'email': email,
                'error': 'Invalid or expired verification code. Please try again.',
            })
