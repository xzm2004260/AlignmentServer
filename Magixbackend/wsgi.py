"""
WSGI config for Magixbackend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Magixbackend.settings")
 
# application = get_wsgi_application() # this is on development

application = Cling(MediaCling(get_wsgi_application())) # allows dj-static to serve static folders, on production