from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
import re

class OnboardingController(http.Controller):

    @http.route('/onboarding', auth='user', website=True)
    def onboarding_main(self, **kw):
        onboarding = request.env['candidate.onboarding'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not onboarding:
            default_template = request.env.ref(
                'candidate_onboarding.default_template'
            )
            onboarding = request.env['candidate.onboarding'].sudo().create({
                'user_id': request.env.user.id,
                'template_id': default_template.id
            })

        steps = onboarding.template_id.step_ids.sorted('sequence')

        return request.render('candidate_onboarding.onboarding_main', {
            'onboarding': onboarding,
            'current_step': onboarding.current_step_id,
            'completed_steps': onboarding.completed_step_ids,
            'remaining_steps': steps - onboarding.completed_step_ids,
            'progress': len(onboarding.completed_step_ids) / len(steps) * 100,
        })

    def _validate_step_data(self, onboarding, post):
        """Validate form data based on current step"""
        current_step = onboarding.current_step_id.name

        if current_step == 'Personal Information':
            if not re.match(r'^[a-zA-Z ]{2,}$', post.get('first_name', '')):
                raise ValidationError("Enter a valid first name (letters only)")

        elif current_step == 'Contact Details':
            if not re.match(r'^\+?[\d ]{8,}$', post.get('phone', '')):
                raise ValidationError("Enter a valid phone number")

        elif current_step == 'Documents':
            for field in ['cv', 'cover_letter']:
                file = post.get(field)
                if file:
                    if not file.filename.lower().endswith('.pdf'):
                        raise ValidationError(f"{field.replace('_',' ').title()} must be a PDF file")

    @http.route('/onboarding/save', auth='user', website=True, methods=['POST'])
    def save_step_data(self, **post):
        onboarding = request.env['candidate.onboarding'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not onboarding:
            return request.redirect('/onboarding')

        try:
            # Validate before saving
            self._validate_step_data(onboarding, post)

            # Save form data
            values = {}
            for field in post:
                if field in onboarding._fields and not field.startswith('_'):
                    values[field] = post[field]

            # Handle file uploads separately
            for field in ['cv', 'cover_letter']:
                file = post.get(field)
                if file:
                    values[field] = file.read()
                    values[f"{field}_filename"] = file.filename

            onboarding.write(values)

            # Handle navigation
            if post.get('next_step'):
                onboarding.action_next_step()
            elif post.get('prev_step'):
                onboarding.action_prev_step()

        except ValidationError as e:
            return request.render('candidate_onboarding.onboarding_main', {
                'onboarding': onboarding,
                'error': str(e),
                'current_step': onboarding.current_step_id,
                'completed_steps': onboarding.completed_step_ids,
                'remaining_steps': onboarding.template_id.step_ids.sorted('sequence') - onboarding.completed_step_ids,
                'progress': len(onboarding.completed_step_ids) / len(onboarding.template_id.step_ids) * 100,
            })

        return request.redirect('/onboarding')
