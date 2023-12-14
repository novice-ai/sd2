from os import environ

SESSION_CONFIGS = [
     {
        'name': 'test',
        'display_name': 'test',
        'app_sequence': ['test'],
        'num_demo_participants': 2,
   
    }
]

SESSION_CONFIG_DEFAULTS = {
    'name': 'My Default Session',
    'participation_fee': 0,
    'display_name': 'Default Session',
    'num_demo_participants': 6,
    'real_world_currency_per_point': 1/7,
    'name': 'sd-cb',
    'display_name': "sd-cb",
    'num_demo_participants': 6,
    'use_firm_belief_elicitation': True,
    'use_worker_belief_elicitation': True,
    'num_first_stage_rounds': 10,
    'num_second_stage_rounds': 10,
    'num_third_stage_rounds': 10,
    'num_fourth_stage_rounds': 10,
    'real_world_currency_per_point': 1/7,
    'app_sequence': ['test'],
    'participation_fee': 100,
    'type_disclosure': True,
    'costly_signaling': True
}

# Additional oTree configurations and settings go here
LANGUAGE_CODE = 'zh-tw'
USE_POINTS = True
POINTS_CUSTOM_NAME = '法幣'
SECRET_KEY = ''
ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
if environ.get('OTREE_PRODUCTION') not in {None, '', '0'}:
    DEBUG = True
else:
    DEBUG = False
DEFAULT_CHARSET = 'UTF-8'

# Define other settings as needed
INSTALLED_APPS = ['otree']
