from os import environ

SESSION_CONFIGS = [
    # dict(
    #     name='public_goods',
    #     app_sequence=['public_goods'],
    #     num_demo_participants=3,
    # ),
     dict(
        name='Basic_PD_ATA_Router',
        display_name = 'Basic PD ATA Router',
        app_sequence=['Basic_PD_ATA_Router',  'Basic_PD_ATA', 'Basic_PD_ATA_Simple', 'Basic_SH', 'Basic_SH_Simple'],
        num_demo_participants=2,
        # room = 'Basic_PD_ATA_Router',
        prolific_completion_url = 'https://app.prolific.com/submissions/complete?cc=C1K54SMD',
    ),
     dict(
        name='Basic_PD_ATA',
        display_name = 'Basic PD ATA',
        app_sequence=['Basic_PD_ATA'],
        num_demo_participants=2,
        prolific_completion_url = 'https://app.prolific.com/submissions/complete?cc=123ABC45',
    ),
    #  dict(
    #     name='Basic_PD_ATA_Simple',
    #     display_name = 'Basic PD ATA Simple',
    #     app_sequence=['Basic_PD_ATA_Simple'],
    #     num_demo_participants=2,
    #     prolific_completion_url = 'https://app.prolific.com/submissions/complete?cc=123ABC45',
    # ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['is_dropout']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '7056942908644'

## Rooms
ROOMS = [
    dict(
        name = 'Basic_PD_ATA_Router',
        display_name = 'Basic PD ATA Rooms',
        #participant_label_file = '_rooms/basic_pd_ata_room.txt',
        #use_secure_urls = False
    ),

]