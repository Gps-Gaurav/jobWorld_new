from pathlib import Path
from decouple import config
import os
import cloudinary
import cloudinary.uploader
from decouple import config

cloudinary.config(
  cloud_name=config("CLOUDINARY_CLOUD_NAME"),
  api_key=config("CLOUDINARY_API_KEY"),
  api_secret=config("CLOUDINARY_API_SECRET")
)
# Project ka base directory set karo
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# Basic Environment Settings
# ------------------------------

# Secret key for security (production me strong key use karo)
SECRET_KEY = config('ACCESS_TOKEN_SECRET', default='your-secret-key')

# Debug mode (development me True, production me False)
DEBUG = config('DEBUG', default=True, cast=bool)

# Allowed domains jo Django server access kar sakte hain
ALLOWED_HOSTS = ['*']  # Production me specific domain likhna better hota hai

# ------------------------------
# Installed Applications
# ------------------------------

INSTALLED_APPS = [
    # Django ke core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd-party apps
    'rest_framework',
    'corsheaders',

    # Apne khud ke apps
    'core',
    'api',
]

# ------------------------------
# Middleware
# ------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Cross-Origin headers
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom middleware agar tumne banaye ho
    'core.middleware.RequestLogMiddleware',
    'api.middleware.RequestLoggingMiddleware',
]

# ------------------------------
# REST Framework Config
# ------------------------------

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': [
       'api.utils.jwt_auth.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Har route protected by default
    ]
}

# ------------------------------
# URL and WSGI Config
# ------------------------------

ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'

# ------------------------------
# Template Config
# React ka dist/index.html render karwane ke liye yeh zaroori hai
# ------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR /'templates'],
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

# ------------------------------
# Database Config (MongoDB using djongo)
# ------------------------------

DATABASES = {
    
}

# ------------------------------
# CORS Config (frontend se API call allow karne ke liye)
# ------------------------------

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:4000",
    "https://jobworld-new.onrender.com",
    config('FRONTEND_URL', default='http://localhost:5173'),
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
APPEND_SLASH = False
# ------------------------------
# Static Files (React ke build assets serve karne ke liye)
# ------------------------------

STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#     BASE_DIR / 'frontend' / 'dist' / 'assets'
# ]

# ------------------------------
# Email Configuration (Gmail SMTP)
# ------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD', default='')

# ------------------------------
# Cloudinary Setup (agar use kar rahe ho images ke liye)
# ------------------------------

CLOUDINARY = {
    'cloud_name': config('CLOUDINARY_CLOUD_NAME', default=''),
    'api_key': config('CLOUDINARY_API_KEY', default=''),
    'api_secret': config('CLOUDINARY_API_SECRET', default=''),
}

# ------------------------------
# Password Validation
# ------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------
# Internationalization Settings
# ------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ------------------------------
# Default Primary Key Field
# ------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
