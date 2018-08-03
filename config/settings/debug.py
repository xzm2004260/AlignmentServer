from .base import *

DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY','8lu*7g0lg)9z!ba+a$ehk)xt)x%rxgb$i1&amp;022shmi1jcgihb*')

WSGI_APPLICATION = 'config.test_wsgi.application'





REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}
