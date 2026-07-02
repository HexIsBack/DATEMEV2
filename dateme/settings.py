from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'some-very-secret-key-for-development-only'
DEBUG = True
ALLOWED_HOSTS = ['*']

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
    'default':  {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'users.sqlite3'},
    'chat_db':  {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'chat.sqlite3'},
    'media_db': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'media.sqlite3'},
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
EMAIL_HOST_USER     = 'your_email_for_password_reset@gmail.com'
EMAIL_HOST_PASSWORD = 'api=your_app_password_here'  # Use an app password for Gmail     
DEFAULT_FROM_EMAIL  = 'DateMe <your_email_for_password_reset@gmail.com>'

# Reset link expires after 24 hours
PASSWORD_RESET_TIMEOUT = 86400
