
"""Magixbackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
settings_name = os.environ.get('DJANGO_SETTINGS_MODULE')
if settings_name == 'Magixbackend.settings.test':
    from Magixbackend.settings import test as settings
elif settings_name == 'Magixbackend.settings.production':
    from Magixbackend.settings import production as settings

from django.contrib import admin
from django.conf.urls import url, include

    

from django.conf.urls.static import static


urlpatterns = [
    url('admin/', admin.site.urls),
    url('^auth/', include('authentication.urls')),
    url('^alignments/', include('alignment.urls')),
    url('^compositions/', include('composition.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
