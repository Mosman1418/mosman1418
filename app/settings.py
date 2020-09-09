# Django settings for mosman1418 project.
import os
gettext = lambda s: s
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SITE_ID = 1
ADMINS = (
    # ('Tim Sherratt', 'tim@discontents.com.au'),
    ('Sachit Adhikari', 'adhikarisachit@gmail.com'),
)


ALLOWED_HOSTS = ['*']

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
         'NAME': 'mosman1914django',                      # Or path to database file if using sqlite3.
         'USER': 'root',                      # Not used with sqlite3.
         'PASSWORD': '',                  # Not used with sqlite3.
         'HOST': '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',                      # Set to empty string for localhost. Not used with sqlite3.
         'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
     }
}
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH,'media/')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/mosman1914/app/static/'
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, "static"),
    os.path.join(PROJECT_PATH, "app/static"),

)


# Make this unique, and don't share it with anybody.
SECRET_KEY = '&amp;o^%i4tsp8!2%nf2yj6s#*7o_!a&amp;la=rgcoqk$b-=2g3!(gue*'


# List of callables that know how to import templates from various sources.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_PATH, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# List of callables that know how to import templates from various sources.

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    #'cms.context_processors.media',
    #'sekizai.context_processors.sekizai',
)


CMS_TEMPLATES = (
    ('cms_template_1.html', 'Template One'),
    ('cms_template_2.html', 'Template Two'),
)

LANGUAGES = [
    ('en', 'English'),
]

AUTHENTICATION_BACKENDS = (
    #'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

ANONYMOUS_USER_ID = -1

#LOGIN_REDIRECT_URL = '/'

ROOT_URLCONF = 'app.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'app.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    #'cms',
    #'mptt',
    #'menus',
    #'south',
    #'sekizai',
    'reversion',
    'guardian',
    'django_registration',
    #'cms.plugins.googlemap',
    #'cms.plugins.link',
    #'cms.plugins.text',
    #'cms.plugins.twitter',
    #'filer',
    #'cmsplugin_filer_file',
    #'cmsplugin_filer_folder',
    #'cmsplugin_filer_image',
    #'cmsplugin_filer_teaser',
    #'cmsplugin_filer_video',
    'django_select2',
    'easy_thumbnails',
    'django_extensions',
    'ckeditor',
    'app.templatetags',
    'app.memorials',
    'app.people',
    'app.events',
    'app.places',
    'app.objects',
    'app.sources',
    'app.linkeddata',
)

THUMBNAIL_DEBUG = False

ACCOUNT_ACTIVATION_DAYS = 7

AUTO_RENDER_SELECT2_STATICS = False
ENABLE_SELECT2_MULTI_PROCESS_SUPPORT = True
SELECT2_BOOTSTRAP = True

#MAIL_HOST = 'smtp.anchor.net.au'
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''


DEFAULT_FROM_EMAIL = 'admin@mosman1914-1918.net' 

CKEDITOR_UPLOAD_PATH = '/home/mosman1914/app/media'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 
            [
                { 'name': 'clipboard',   'items' : [ 'Source', 'Cut','Copy','Paste','PasteText','PasteFromWord','-','Undo','Redo' ] },
                { 'name': 'editing',     'items' : [ 'SelectAll', 'Link', 'Unlink'] },
                { 'name': 'basicstyles', 'items' : [ 'Bold','Italic','Underline','Strike','Subscript','Superscript','-','RemoveFormat' ] },
                { 'name': 'paragraph',   'items' : [ 'NumberedList','BulletedList','-','Outdent','Indent','-','Blockquote' ] },
            ],
        'width': '50%',
        'height': 200,
        'forcePasteAsPlainText': True
    },
}

