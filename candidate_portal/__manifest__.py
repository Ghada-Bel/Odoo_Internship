# -*- coding: utf-8 -*-
{
    'name': "candidate_portal",
    'summary': "Portal for candidate registration and verification",
    'description': """
        Candidate portal that allows users to sign up and verify via email.
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'website', 'mail','auth_signup'],  

    'data': [
        'security/ir.model.access.csv',
        'views/signup_template.xml',
        'views/candidate_views.xml',
        'views/website_layout_templates.xml',
        'views/verify_template.xml',
        'views/success_template.xml',
        'views/login_template_inherit.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'candidate_portal/static/src/js/signup_validation.js',
	    'https://cdn.jsdelivr.net/npm/intl-tel-input@18.1.1/build/css/intlTelInput.min.css',
            'https://cdn.jsdelivr.net/npm/intl-tel-input@18.1.1/build/js/intlTelInput.min.js',
 	    
        ],
    },

    'demo': ['demo/demo.xml'],
    'installable': True,
    'application': True,
}
