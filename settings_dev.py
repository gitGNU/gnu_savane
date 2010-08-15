# Import sane defaults:
from settings_default import *

# Don't send e-mails for real, display them on the console:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Alternatively, local mailbox:
#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/tmp/app-messages' # change this to a proper location
# Alternatively: in memory, with an interface at localhost:8000/dev/webmail/
#EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Configure database access
DATABASES = {
    'default': {
        'NAME': 'savane',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'savane',
        'PASSWORD': 'savane',
    }
}

# Your other configuration parameters here (cf. settings_default).
