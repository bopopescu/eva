#!/usr/bin/python
# -*-coding:utf-8-*-
"""
Django settings for cmdb project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*@tw#**f5&q*y2!$ry5=mr^k_o*-)$zjp@hy%q_ws%f%-(%v0d'
auth_key = '*@tw#**f5&q*y2!$ry5=mr^k_o*-)$zjp@hy%q_ws%f%-(%v0d'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

#ALLOWED_HOSTS = ["127.0.0.1"]
ALLOWED_HOSTS = ['*']
LOGIN_REDIRECT_URL = "/index/"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'cmdb_auth',
    'bootstrapform',
    'bootstrap3',
    'assets',
    'Allow_list',
    'business',
    'automation',



]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cmdb.urls'
AUTH_USER_MODEL = 'accounts.CustomUser'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'cmdb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cmdb_v1',
        'USER': 'root',
        'PASSWORD': 'VBkLG6UqrqKD9QDYwwfZ',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        "OPTIONS": {
            'charset': 'utf8mb4',
            "init_command": "SET foreign_key_checks = 0;",
    	}
	}
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    ('js', os.path.join(STATIC_ROOT, 'js').replace('\\', '/')),
    ('admin-test', os.path.join(STATIC_ROOT, 'admin-test').replace('\\', '/')),
    ('css', os.path.join(STATIC_ROOT, 'css').replace('\\', '/')),
    ('images', os.path.join(STATIC_ROOT, 'images').replace('\\', '/')),
    ('bootstrap', os.path.join(STATIC_ROOT, 'bootstrap').replace('\\', '/')),
    ('layer', os.path.join(STATIC_ROOT, 'layer').replace('\\', '/')),
    ('layer-v2.4', os.path.join(STATIC_ROOT, 'layer-v2.4').replace('\\', '/')),
    ('valodate', os.path.join(STATIC_ROOT, 'valodate').replace('\\', '/')),

    ]

# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' 
EMAIL_PORT = 587
EMAIL_HOST_USER = 'whf2chen@gmail.com'
EMAIL_HOST_PASSWORD = 'whf7chen' 
EMAIL_SUBJECT_PREFIX = u'[自动化运维系统]' 
DEFAULT_FROM_EMAIL = 'devops <devops@123.com>'
EMAIL_USE_TLS = True
EMAIL_PUSH = True

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE= 'Asia/Shanghai'

ANSIBLE_ROLES_DIR='/root/myproject/cmdb/ansible_workdir/'
