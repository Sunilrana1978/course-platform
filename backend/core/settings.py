from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'apps.users',
    'apps.courses',
    'apps.cart',
    'apps.subscriptions',
    'apps.payments',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'core.urls'

import tempfile, os as _os

# Ephemeral SQLite — resets each time start.sh is run (same semantics as in-memory).
# To use Postgres: replace ENGINE and NAME below, add HOST/PORT/USER/PASSWORD.
_DB_PATH = _os.environ.get('DB_PATH', _os.path.join(tempfile.gettempdir(), 'course_platform_dev.db'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _DB_PATH,
    }
}

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

CORS_ALLOW_ALL_ORIGINS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Payment gateway config — swap to 'paypal' etc. without touching code
PAYMENT_GATEWAY = os.environ.get('PAYMENT_GATEWAY', 'stripe')
MOCK_FAILURE_RATE = float(os.environ.get('MOCK_FAILURE_RATE', '0.05'))
