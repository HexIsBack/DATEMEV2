import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Loads variables from a local .env file (this file is git-ignored).
# On Vercel, .env doesn't exist — the variables come from the
# Environment Variables you set in the Vercel dashboard instead.
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-only-key-do-not-use-in-production',
)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'profiles',
    'matching',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.UpdateLastSeenMiddleware',
]

ROOT_URLCONF = 'dateme.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages',]},}]
WSGI_APPLICATION = 'dateme.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'users.sqlite3'}",
        env='DATABASE_URL',
        conn_max_age=600,
    ),
    'chat_db': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'chat.sqlite3'}",
        env='CHAT_DATABASE_URL',
        conn_max_age=600,
    ),
    'media_db': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'media.sqlite3'}",
        env='MEDIA_DATABASE_URL',
        conn_max_age=600,
    ),
}

DATABASE_ROUTERS = ['dateme.routers.AppRouter']

# ── Sessions ────────────────────────────────────────────────────────────
# Explicitly use the database backend and pin it to the 'default' DB.
# This prevents SessionInterrupted errors caused by the multi-DB setup.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600          # 2 weeks, in seconds
SESSION_SAVE_EVERY_REQUEST = False    # only save when modified (default)

AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_REDIRECT_URL = '/profiles/setup/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Password Reset Email ────────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('DATEME_EMAIL', '')
EMAIL_HOST_PASSWORD = os.environ.get('DATEME_EMAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL  = f'DateMe <{EMAIL_HOST_USER}>'

# Reset link expires after 24 hours
PASSWORD_RESET_TIMEOUT = 86400