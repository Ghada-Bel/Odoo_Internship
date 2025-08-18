{
    'name': 'Base Theme Assets',
    'version': '1.0',
    'summary': 'Common CSS assets for all custom modules',
    'description': 'Includes shared CSS like header/footer styling',
    'author': 'Your Name',
    'category': 'Hidden',
    'depends': ['web'],  
    'data': [],
    'assets': {
        'web.assets_frontend': [
            'base_theme/static/src/css/common.css',
        ],
    },
    'installable': True,
    'application': True,
}
