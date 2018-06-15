from .base import *

DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY','8lu*7g0lg)9z!ba+a$ehk)xt)x%rxgb$i1&amp;022shmi1jcgihb*')

WSGI_APPLICATION = 'Magixbackend.test_wsgi.application'





DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), BASE_DIR.child('db.sqlite3')), # no name means in-memory but in-memory does not support threads
        'TEST_NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
        'OPTIONS': {'timeout': 30},
    }
  }


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}
