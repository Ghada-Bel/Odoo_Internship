# -*- coding: utf-8 -*-
import base64
import re
from datetime import datetime

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError


class OnboardingController(http.Controller):

    @http.route('/onboarding', auth='user', website=True)
    def onboarding_main(self, **kw):
        onboarding = request.env['candidate.onboarding'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not onboarding:
            # Get or create default template
            default_template = request.env.ref('candidate_onboarding.default_template', raise_if_not_found=False)
            if not default_template:
                # Create a basic template if it doesn't exist
                default_template = request.env['onboarding.template'].sudo().create({
                    'name': 'Default Candidate Onboarding',
                    'description': 'Standard onboarding process for candidates'
                })
                # Create default steps
                steps_data = [
                    {'name': 'Personal Information', 'sequence': 10},
                    {'name': 'Additional Information', 'sequence': 20},
                    {'name': 'Highest Qualification', 'sequence': 30},
                    {'name': 'Other Qualifications', 'sequence': 40},
                    {'name': 'Work Experience', 'sequence': 50},
                    {'name': 'Skills', 'sequence': 60},
                    {'name': 'Availability', 'sequence': 70},
                    {'name': 'References', 'sequence': 80},
                    {'name': 'Documents', 'sequence': 90},
                ]
                for step_data in steps_data:
                    step_data['template_id'] = default_template.id
                    request.env['onboarding.step'].sudo().create(step_data)
            
            onboarding = request.env['candidate.onboarding'].sudo().create({
                'user_id': request.env.user.id,
                'template_id': default_template.id,
                'email': request.env.user.email or '',
                'first_name': request.env.user.name.split(' ')[0] if request.env.user.name else '',
                'surname': ' '.join(request.env.user.name.split(' ')[1:]) if request.env.user.name and len(request.env.user.name.split(' ')) > 1 else '',
            })

        steps = onboarding.template_id.step_ids.sorted('sequence')
        total_steps = len(steps)
        completed_count = len(onboarding.completed_step_ids)
        progress = (completed_count / max(total_steps, 1)) * 100

        return request.render('candidate_onboarding.onboarding_main', {
            'onboarding': onboarding,
            'current_step': onboarding.current_step_id,
            'completed_steps': onboarding.completed_step_ids,
            'remaining_steps': steps - onboarding.completed_step_ids,
            'progress': progress,
            'total_steps': total_steps,
            'error': kw.get('error'),
        })

    def _validate_step_data(self, onboarding, post, files):
        """Validate form data for the current step."""
        step_name = (onboarding.current_step_id.name or '').strip()

        if step_name == 'Personal Information':
            # Validate first name
            first_name = post.get('first_name', '').strip()
            if not first_name or not re.match(r'^[a-zA-Z\s]{2,}$', first_name):
                raise ValidationError("Please enter a valid first name (letters only, minimum 2 characters).")
            
            # Validate surname
            surname = post.get('surname', '').strip()
            if not surname or not re.match(r'^[a-zA-Z\s]{2,}$', surname):
                raise ValidationError("Please enter a valid surname (letters only, minimum 2 characters).")
            
            # Validate ID number
            id_number = post.get('id_number', '').strip()
            if not id_number:
                raise ValidationError("ID Number is required.")
            
            # Validate email
            email = post.get('email', '').strip()
            if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError("Please enter a valid email address.")
            
            # Validate gender
            if not post.get('gender'):
                raise ValidationError("Please select your gender.")
            
            # Validate date of birth
            dob = post.get('date_of_birth')
            if not dob:
                raise ValidationError("Date of birth is required.")
            try:
                dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                today = datetime.today().date()
                age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                if age < 16 or age > 100:
                    raise ValidationError("Please enter a valid date of birth.")
            except ValueError:
                raise ValidationError("Please enter a valid date of birth.")
            
            # Validate marital status
            if not post.get('marital_status'):
                raise ValidationError("Please select your marital status.")
            
            # Validate dependencies
            try:
                dependencies = int(post.get('dependencies', 0))
                if dependencies < 0:
                    raise ValidationError("Number of dependencies cannot be negative.")
            except (ValueError, TypeError):
                raise ValidationError("Please enter a valid number for dependencies.")

        elif step_name == 'Additional Information':
            # Validate phone if provided
            phone = post.get('phone', '').strip()
            if phone and not re.match(r'^\+?[\d\s\-\(\)]{8,}$', phone):
                raise ValidationError("Please enter a valid phone number.")
            
            # Validate country
            if not post.get('country'):
                raise ValidationError("Please select your country.")

        elif step_name == 'Highest Qualification':
            # Validate qualification level
            if not post.get('qualification_level'):
                raise ValidationError("Please select your highest qualification level.")
            
            # Validate qualification field
            if not post.get('qualification_field', '').strip():
                raise ValidationError("Please enter your qualification field/subject.")
            
            # Validate institution
            if not post.get('institution', '').strip():
                raise ValidationError("Please enter the institution name.")

        elif step_name == 'Documents':
            # Validate file uploads
            for field in ('cv', 'cover_letter'):
                file_upload = files.get(field)
                if file_upload:
                    filename = (file_upload.filename or '').lower()
                    content_type = (file_upload.content_type or '').lower()
                    if not filename.endswith('.pdf') or 'pdf' not in content_type:
                        field_name = field.replace('_', ' ').title()
                        raise ValidationError(f"{field_name} must be a PDF file.")
                    
                    # Check file size (max 5MB)
                    file_upload.seek(0, 2)  # Seek to end
                    file_size = file_upload.tell()
                    file_upload.seek(0)  # Seek back to beginning
                    if file_size > 5 * 1024 * 1024:  # 5MB
                        field_name = field.replace('_', ' ').title()
                        raise ValidationError(f"{field_name} must be smaller than 5MB.")

    @http.route('/onboarding/save', auth='user', website=True, methods=['POST'], csrf=True)
    def save_step_data(self, **post):
        onboarding = request.env['candidate.onboarding'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not onboarding:
            return request.redirect('/onboarding')

        files = request.httprequest.files
        try:
            # Validate the step data
            self._validate_step_data(onboarding, post, files)

            # Prepare values to update
            vals = {}

            # Map form fields to model fields
            field_mapping = {
                'first_name': 'first_name',
                'surname': 'surname', 
                'id_number': 'id_number',
                'email': 'email',
                'gender': 'gender',
                'date_of_birth': 'date_of_birth',
                'marital_status': 'marital_status',
                'dependencies': 'dependencies',
                'country': 'country',
                'phone': 'phone',
                'physical_address': 'physical_address',
                'citizenship': 'citizenship',
                'birthplace': 'birthplace',
                'field_id': 'field_id',
                'occupation': 'occupation',
                'next_of_kin': 'next_of_kin',
                'qualification_level': 'qualification_level',
                'qualification_field': 'qualification_field',
                'institution': 'institution',
                'qualification_year': 'qualification_year',
                'start_date': 'start_date',
                'notice_period': 'notice_period',
            }

            # Process regular fields
            for form_field, model_field in field_mapping.items():
                if form_field in post and model_field in onboarding._fields:
                    value = post[form_field].strip() if isinstance(post[form_field], str) else post[form_field]
                    if value:  # Only update if value is not empty
                        # Handle special field types
                        if model_field in ['dependencies', 'qualification_year', 'notice_period']:
                            try:
                                vals[model_field] = int(value)
                            except (ValueError, TypeError):
                                vals[model_field] = 0
                        elif model_field in ['country', 'field_id'] and value.isdigit():
                            vals[model_field] = int(value)
                        else:
                            vals[model_field] = value

            # Handle file uploads
            for file_field in ('cv', 'cover_letter', 'id_document', 'certificates'):
                file_upload = files.get(file_field)
                if file_upload and file_upload.filename:
                    content = file_upload.read()
                    vals[file_field] = base64.b64encode(content)
                    vals[f"{file_field}_filename"] = file_upload.filename

            # Update the onboarding record
            if vals:
                onboarding.sudo().write(vals)

            # Handle step navigation
            if post.get('next_step'):
                onboarding.action_next_step()
            elif post.get('prev_step'):
                onboarding.action_prev_step()

        except ValidationError as e:
            # Return to form with error message
            steps = onboarding.template_id.step_ids.sorted('sequence')
            total_steps = len(steps)
            completed_count = len(onboarding.completed_step_ids)
            progress = (completed_count / max(total_steps, 1)) * 100
            
            return request.render('candidate_onboarding.onboarding_main', {
                'onboarding': onboarding,
                'current_step': onboarding.current_step_id,
                'completed_steps': onboarding.completed_step_ids,
                'remaining_steps': steps - onboarding.completed_step_ids,
                'progress': progress,
                'total_steps': total_steps,
                'error': str(e),
            })

        return request.redirect('/onboarding')

    @http.route('/onboarding/complete', auth='user', website=True)
    def onboarding_complete(self, **kw):
        """Final completion page"""
        onboarding = request.env['candidate.onboarding'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not onboarding or onboarding.state != 'completed':
            return request.redirect('/onboarding')
        
        return request.render('candidate_onboarding.onboarding_complete', {
            'onboarding': onboarding,
        })
