# Django settings for savane project.

from django.conf import global_settings
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'savane',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# http://docs.djangoproject.com/en/dev/topics/i18n/deployment/#how-django-discovers-language-preference
ugettext = lambda s: s
LANGUAGES = (
    ('ca',    ugettext('Catalan')),
    ('de',    ugettext('German')),
    ('en',    ugettext('English')),
    ('es',    ugettext('Spanish')),
    ('fr',    ugettext('French')),
    ('it',    ugettext('Italian')),
    ('ja',    ugettext('Japanese')),
    ('pt_BR', ugettext('Portuguese (Brazil)')),
    ('ru',    ugettext('Russian')),
    ('sv',    ugettext('Swedish')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_L10N=True

# Make this unique, and don't share it with anybody.
# TODO: re-generate this on first install, or something
SECRET_KEY = 'r0u=mcmr$46vf6y3x4!lti5pza)p-3y@*u%5k!71)ie)1dha@$'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'savane.context_processors.media',
    'savane.context_processors.site_name',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'savane.middleware.debug.DebugFooter',
    'savane.middleware.exception.HttpCatchAppExceptionMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
)

# Used by syncdb, etc.
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',

    'django.contrib.admin',
    'django.contrib.admindocs',

    'registration',

    'savane.svmain',
    'savane.my',
    'savane.svpeople',
    'savane.tracker',
)


# Paths
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/my/'

# Applications media
STATIC_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static_media/')
STATIC_MEDIA_URL = '/static_media/'

# Media for Django auto-admin
ADMIN_MEDIA_PREFIX = '/admin_media/'

# User-uploaded media (with trailing slashes)
MEDIA_ROOT = os.path.dirname(__file__) + '/upload/'
MEDIA_URL = '/upload/'

# For a subdir:
#subdir = '/savane'
#LOGIN_URL          = subdir + '/accounts/login/'
#LOGIN_REDIRECT_URL = subdir + '/'
#REQUIRE_LOGIN_PATH = LOGIN_URL
#STATIC_MEDIA_URL   = subdir + '/static_media/'
#MEDIA_URL          = subdir + '/upload/'


# E-mail
#DEFAULT_FROM_EMAIL='webmaster@localhost'


# 3rd-party configuration

# django-registration
ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window
