"""
Django settings for smllr project.

Generated by 'django-admin startproject' using Django 5.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os

from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o9r=_&sgxo@aagjyxh7%7pa=qiktyg-$-)e5s6zefg+m26v-42'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', 'yes', '1']

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

PUBLIC_URL = os.getenv('PUBLIC_URL', 'http://127.0.0.1:8000')

# CSRF for production
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')


# Application definition

INSTALLED_APPS = [
    'smllr.core',
    'smllr.shorturls',
    'smllr.users',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'smllr.shorturls.middlewares.UserMetadataMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'smllr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'smllr' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'smllr.shorturls.context_processors.conf',
                'smllr.users.context_processors.social_account',
                'smllr.users.context_processors.feature_toggle',
            ],
        },
    },
]

STATICFILES_DIRS = [
    BASE_DIR / 'smllr' / 'static',
]

STATIC_ROOT = BASE_DIR / 'static'

STATIC_URL = 'static/'

WSGI_APPLICATION = 'smllr.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if os.getenv('DATABASE_ENGINE') == 'postgresql':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'smllr'),
        'USER': os.getenv('DATABASE_USER', 'root'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'root'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Custom user model

AUTH_USER_MODEL = 'users.User'


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Short URL created by anonymous users limit

MAX_SHORTURLS_PER_ANON_USER = 5

SHORTURL_EXPIRATION_TIME_DAYS = int(os.getenv('SHORTURL_EXPIRATION_TIME_DAYS', 30))

# Django Allauth settings

ALLOW_SOCIAL_LOGIN = os.getenv('ALLOW_SOCIAL_LOGIN', 'True').lower() in ['true', 'yes', '1']

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
        'FETCH_USERINFO' : True,
        'APPS': [
            {
                'client_id': os.getenv('GOOGLE_CLIENT_ID', 'your-client-id'),
                'secret': os.getenv('GOOGLE_CLIENT_SECRET', 'your-client-secret'),
            }
        ],
    },
    'github': {
        'SCOPE': [
            'read:user',
            'user:email',
        ],
        'OAUTH_PKCE_ENABLED': True,
        'FETCH_USERINFO' : True,
        'APPS': [
            {
                'client_id': os.getenv('GITHUB_CLIENT_ID', 'your-client-id'),
                'secret': os.getenv('GITHUB_CLIENT_SECRET', 'your-client-secret'),
            }
        ]
    }
}

SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

SOCIALACCOUNT_ADAPTER = 'smllr.users.adapters.SocialAccountAdapter'

ACCOUNT_ADAPTER = 'smllr.users.adapters.AccountAdapter'

LOGIN_REDIRECT_URL = '/'

ACCOUNT_LOGOUT_REDIRECT_URL = '/'

SOCIALACCOUNT_LOGIN_ON_GET = True

ACCOUNT_EMAIL_VERIFICATION = 'none'

SOCIALACCOUNT_ONLY = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if os.getenv('USE_HTTPS', 'True').lower() in ['true', 'yes', '1'] else 'http'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
