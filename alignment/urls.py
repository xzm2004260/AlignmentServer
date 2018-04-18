from django.conf.urls import url
from django.contrib import admin
from .views import (
    CreateAlignmentAPIView,
    AlignmentDetailAPIView,
    UploadAPIView
)


urlpatterns = [
    url('^$', CreateAlignmentAPIView.as_view(), name='create-alignment'),
    url('^upload$', UploadAPIView.as_view(), name='upload-audio'),
    url('^(?P<pk>[0-9]+)$', AlignmentDetailAPIView.as_view(), name='alignment-detail'),
]

