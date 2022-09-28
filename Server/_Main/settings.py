import json
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y1s&0p5h!u*=huoco0&&yn@9um91j%+g%u7%i44bu(b+uuuq7r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Connection

ALLOWED_HOSTS = [
 'localhost',
 '127.0.0.1',
]

#CORS
CORS_ALLOWED_ORIGINS = [
  "http://localhost:8080",
  "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True


# Application definition
INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django_extensions',

  'rest_framework', # REST Framework
  'corsheaders',    # CORS

  'WebClient',      # Статика
]

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  "corsheaders.middleware.CorsMiddleware",
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',

  '_Main.middlewares.api_wrapper_middleware.ApiWrapperMiddleware',
]

ROOT_URLCONF = '_Main.urls'

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['templates'],
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

WSGI_APPLICATION = '_Main.wsgi.application'
ASGI_APPLICATION = "_Main.asgi.application"

CHANNEL_LAYERS = {
  "default": {
    "BACKEND": "channels.layers.InMemoryChannelLayer"
  },
}

REST_FRAMEWORK = {
  'DEFAULT_RENDERER_CLASSES': (
    'rest_framework.renderers.JSONRenderer',
  )
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASE_CONFIG_FILE = '../secret/db.json'

if not os.path.exists(DATABASE_CONFIG_FILE):
  try:
    print(DATABASE_CONFIG_FILE, 'does not exist')
    with open(DATABASE_CONFIG_FILE, 'w'): pass
    print(DATABASE_CONFIG_FILE, 'created in', dir)
  except Exception as e:
    print('DB config error:', e)

with open(DATABASE_CONFIG_FILE, 'r') as config_file:
  try:
    config = json.load(config_file)
  except Exception as e:
    print('DB config error on loading config:' , e)

try:
  DB_NAME = config['DB_NAME']
  USER = config['USER']
  PSWD = config['PSWD']
  HOST = config['HOST']
except KeyError as ke:
  print('DB config error. missing field', ke)

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': DB_NAME,
    'USER': USER,
    'PASSWORD': PSWD,
    'HOST': HOST,
    'PORT': '',
  }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
  os.path.join(BASE_DIR, "../WebClient/build/")
]

print('BASE_DIR:', BASE_DIR)
print('STATIC_ROOT:', STATIC_ROOT)

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,

  'formatters': {
    'verbose-fmt': {
     'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
     'datefmt': '%d-%m-%y %H:%M:%S',
     'style': '{',
    },
    'simple-fmt': {
     'format': '\t[{levelname}]: {asctime} - {message}',
     'datefmt': '%d-%m-%y %H:%M:%S',
     'style': '{',
    },
    'simple-warning-fmt': {
     'format': '[{levelname}]: \t{asctime} - {message}',
     'datefmt': '%d-%m-%y %H:%M:%S',
     'style': '{',
    },
    'connection-fmt': {
     'format': '[CONNECTION]: \t{asctime} - {message}',
     'datefmt': '%d-%m-%y %H:%M:%S',
     'style': '{',
    }
  },

  'handlers': {
   'console': {
    'class': 'logging.StreamHandler',
   },
   'file': {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'filename': 'logs/mainlog.txt',
    'filters': [],
    'formatter': 'simple-fmt'
   },
   'file-warning': {
    'level': 'WARNING',
    'class': 'logging.FileHandler',
    'filename': 'logs/mainlog.txt',
    'filters': [],
    'formatter': 'simple-warning-fmt'
   },
   'file-connection': {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'filename': 'logs/mainlog.txt',
    'filters': [],
    'formatter': 'connection-fmt'
   }
  },

  'filters': {
    'special': {
    },
    'require_debug_true': {
      '()': 'django.utils.log.RequireDebugTrue',
    },
  },

  'loggers': {
   'WebClient.views': {
    'handlers': ['file-connection', 'file-warning'],
    'level': 'INFO',
    'propagate': True,
   },
   'common': {
    'handlers': ['file'],
    'level': 'INFO',
    'propagate': True,
   },
  },

  'root': {
   'handlers': ['console'],
   'level': 'WARNING',
   'propagate': True,
  },
}

GRAPH_MODELS = {
 'all_applications': True,
 'group_models': True,
}
