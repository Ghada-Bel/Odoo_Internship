{
    'name': "candidate_onboarding",
    'summary': "Multi-step form for candidate onboarding",
    'description': """
        Collects candidate data in 9 steps with progress tracking.
    """,
    'author': "Your Name",
    'website': "https://yourcompany.com",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['base','mail','website', 'portal', 'hr'],
    'data': [
 	   'security/ir.model.access.csv',
           'views/onboarding_config_views.xml',
   	    'views/personal_info_step.xml',
	    'views/additional_info_step.xml',
            'views/highest_qualification_step.xml',
	    'views/other_qualifications_step.xml',
   	    'views/work_experience_step.xml',
   	    'views/skills_step.xml',
   	    'views/availability_step.xml',
   	    'views/references_step.xml',
   	    'views/documents_step.xml',
   	    'views/review_step.xml',
   	    'views/onboarding_templates.xml',
	    'views/onboarding_complete.xml',
	    'data/onboarding_steps_data.xml',
],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'candidate_onboarding/static/src/js/onboarding.js',
            'candidate_onboarding/static/src/css/onboarding.css',
        ],
    },
    'installable': True,
    'application': True,
}
