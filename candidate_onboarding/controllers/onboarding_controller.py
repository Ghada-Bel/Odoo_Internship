# -*- coding: utf-8 -*-
import base64
import re
from datetime import datetime

from odoo import http, fields
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
                    {'name': 'Review', 'sequence': 100},
                ]
                for step_data in steps_data:
                    step_data['template_id'] = default_template.id
                    request.env['onboarding.step'].sudo().create(step_data)
            
            # Create onboarding record with fields that match DB schema
            onboarding = request.env['candidate.onboarding'].sudo().create({
                'user_id': request.env.user.id,
                'template_id': default_template.id,
                'first_name': request.env.user.name.split(' ')[0] if request.env.user.name else '',
                'last_name': ' '.join(request.env.user.name.split(' ')[1:]) if request.env.user.name and len(request.env.user.name.split(' ')) > 1 else '',
            })

        steps = onboarding.template_id.step_ids.sorted('sequence')
        total_steps = len(steps)
        completed_count = len(onboarding.completed_step_ids)
        progress = (completed_count / max(total_steps, 1)) * 100

        # Get countries for dropdowns
        countries = request.env['res.country'].sudo().search([])
        
        # Get skills for skills step
        skills = request.env['onboarding.skill'].sudo().search([])

        return request.render('candidate_onboarding.onboarding_main', {
            'onboarding': onboarding,
            'current_step': onboarding.current_step_id,
            'completed_steps': onboarding.completed_step_ids,
            'remaining_steps': steps - onboarding.completed_step_ids,
            'progress': progress,
            'total_steps': total_steps,
            'error': kw.get('error'),
            'countries': countries,
            'skills': skills,
        })

    def _validate_step_data(self, onboarding, post, files):
        """Validate form data for the current step."""
        step_name = (onboarding.current_step_id.name or '').strip()

        if step_name == 'Personal Information':
            # Validate first name
            first_name = post.get('first_name', '').strip()
            if not first_name or not re.match(r'^[a-zA-Z\s]{2,}$', first_name):
                raise ValidationError("Please enter a valid first name (letters only, minimum 2 characters).")
            
            # Validate last name
            last_name = post.get('last_name', '').strip()
            if not last_name or not re.match(r'^[a-zA-Z\s]{2,}$', last_name):
                raise ValidationError("Please enter a valid last name (letters only, minimum 2 characters).")
            
            # Validate ID number
            id_number = post.get('id_number', '').strip()
            if not id_number:
                raise ValidationError("ID Number is required.")
            
            # Validate gender
            if not post.get('gender'):
                raise ValidationError("Please select your gender.")
            
            # Validate date of birth
            dob = post.get('birth_date')  # Changed to match DB field
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
            
            # Validate dependents
            try:
                dependents = int(post.get('dependents', 0))
                if dependents < 0:
                    raise ValidationError("Number of dependents cannot be negative.")
            except (ValueError, TypeError):
                raise ValidationError("Please enter a valid number for dependents.")

        elif step_name == 'Additional Information':
            # Validate phone if provided
            phone = post.get('phone', '').strip()
            if phone and not re.match(r'^\+?[\d\s\-\(\)]{8,}$', phone):
                raise ValidationError("Please enter a valid phone number.")
            
            # Validate country
            if not post.get('country_id'):  # Changed to match DB field
                raise ValidationError("Please select your country.")

        elif step_name == 'Highest Qualification':
            # Validate qualification
            if not post.get('qualification'):
                raise ValidationError("Please enter your highest qualification.")
            
            # Validate field of study
            if not post.get('field_of_study', '').strip():
                raise ValidationError("Please enter your field of study.")
            
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
        
        # Handle edit navigation from review step
        if post.get('edit_step'):
            step_name = post.get('edit_step')
            if onboarding.action_go_to_step(step_name):
                return request.redirect('/onboarding')

        try:
            # Skip validation for Review step
            if onboarding.current_step_id and onboarding.current_step_id.name != 'Review':
                self._validate_step_data(onboarding, post, files)

            # Prepare values to update - Updated to match DB schema exactly
            vals = {}

            # Map form fields to model fields - matching DB columns
            field_mapping = {
                'first_name': 'first_name',
                'last_name': 'last_name',
                'id_number': 'id_number',
                'gender': 'gender',
                'birth_date': 'birth_date',  # Changed from date_of_birth
                'marital_status': 'marital_status',
                'dependents': 'dependents',  # Changed from dependencies
                'country_id': 'country_id',  # Changed from country
                'phone': 'phone',
                'physical_address': 'physical_address',
                'citizenship': 'citizenship',
                'birthplace': 'birthplace',
                'education_field': 'education_field',  # Changed from field_id
                'occupation': 'occupation',
                'next_of_kin': 'next_of_kin',
                'qualification': 'qualification',  # Changed from qualification_level
                'field_of_study': 'field_of_study',  # Changed from qualification_field
                'institution': 'institution',
                'graduation_year': 'graduation_year',  # Changed from qualification_year
                'availability': 'availability',  # Simplified availability fields
                # Skills fields matching DB
                'other_technical_skill': 'other_technical_skill',
                'other_interpersonal_skill': 'other_interpersonal_skill',
                'other_management_skill': 'other_management_skill',
                'other_cognitive_skill': 'other_cognitive_skill',
                'other_personal_attribute': 'other_personal_attribute',
            }

            # Process regular fields
            for form_field, model_field in field_mapping.items():
                if form_field in post and model_field in onboarding._fields:
                    value = post[form_field].strip() if isinstance(post[form_field], str) else post[form_field]
                    if value:  # Only update if value is not empty
                        # Handle special field types
                        if model_field in ['dependents', 'graduation_year']:
                            try:
                                vals[model_field] = int(value)
                            except (ValueError, TypeError):
                                vals[model_field] = 0
                        elif model_field in ['country_id'] and value.isdigit():
                            vals[model_field] = int(value)
                        else:
                            vals[model_field] = value

            # Handle other qualifications
            if 'oq_qualification' in post and post['oq_qualification']:
                qual_vals = {
                    'qualification': post['oq_qualification'],
                    'field_of_study': post.get('oq_field', ''),
                    'institution': post.get('oq_institution', ''),
                    'year': int(post.get('oq_year', 0)) if post.get('oq_year') else None,
                }
                # Clear existing and add new
                onboarding.other_qualification_ids.unlink()
                onboarding.other_qualification_ids = [(0, 0, qual_vals)]

            # Handle work experience
            if 'exp_company' in post and post['exp_company']:
                exp_vals = {
                    'company': post['exp_company'],
                    'position': post.get('exp_position', ''),
                    'start_date': post.get('exp_start_date') if post.get('exp_start_date') else None,
                    'end_date': post.get('exp_end_date') if post.get('exp_end_date') else None,
                    'currently_working': bool(post.get('currently_working')),
                }
                # Clear existing and add new
                onboarding.work_experience_ids.unlink()
                onboarding.work_experience_ids = [(0, 0, exp_vals)]

            # Handle references
            if 'ref_name' in post and post['ref_name']:
                ref_vals = {
                    'name': post['ref_name'],
                    'company': post.get('ref_company', ''),
                    'phone': post.get('ref_phone', ''),
                    'email': post.get('ref_email', ''),
                }
                # Clear existing and add new
                onboarding.reference_ids.unlink()
                onboarding.reference_ids = [(0, 0, ref_vals)]
            # Handle file uploads - only filename fields exist in DB
            for file_field in ('cv', 'cover_letter'):
                file_upload = files.get(file_field)
                if file_upload and file_upload.filename:
                    vals[f"{file_field}_filename"] = file_upload.filename

            # Update the onboarding record
            if vals:
                onboarding.sudo().write(vals)

            # Handle final submission
            if post.get('submit_application'):
                return request.redirect('/onboarding/complete')

            # Handle step navigation
            if post.get('next_step'):
                onboarding.action_next_step()
            elif post.get('prev_step'):
                onboarding.action_prev_step()

        except ValidationError as e:
            # Return to form with error message
            return request.redirect('/onboarding?error=' + str(e))

        return request.redirect('/onboarding')

    @http.route('/onboarding/complete', auth='user', website=True)
    def onboarding_complete(self, **kw):
        """Final completion page"""
        onboarding = request.env['candidate.onboarding'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not onboarding:
            return request.redirect('/onboarding')
        
        return request.render('candidate_onboarding.onboarding_complete', {
            'onboarding': onboarding,
        })
