from django.conf.urls import url
from django.contrib import admin
from .views import CreateAlignmentAPIView, AlignmentDetailAPIView


urlpatterns = [
    url('^$', CreateAlignmentAPIView.as_view(), name='create-alignment'),
    url('^(?P<pk>[0-9]+)$', AlignmentDetailAPIView.as_view(), name='alignment-detail'),
]
