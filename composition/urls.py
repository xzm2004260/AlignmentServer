from django.conf.urls import url
from .views import CompositionCreateAPIView


urlpatterns = [
    url(r'^$', CompositionCreateAPIView.as_view()),
]

