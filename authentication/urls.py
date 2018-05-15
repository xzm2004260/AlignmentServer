from django.conf.urls import url
from authentication.views import ChangePasswordView, UserSignInAPIView


urlpatterns = [
    url('^password/change$', ChangePasswordView.as_view(), name='password-change'),
    url('^token$', UserSignInAPIView.as_view(), name='token'),
]

