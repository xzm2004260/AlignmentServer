from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions
from services.jwt_helper import JWTHelper


User = get_user_model()


class UserAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            token = request.META.get('HTTP_AUTHORIZATION').replace("Bearer ", "")
            if not token:
                raise exceptions.AuthenticationFailed('No-token-provided')
            is_valid, message = JWTHelper.is_token_valid(token)
            if is_valid:
                user = JWTHelper.decode_token(token)
                if user:
                    return user, None
                raise exceptions.AuthenticationFailed('Authentication Failed')
            raise exceptions.AuthenticationFailed(message)
        raise exceptions.AuthenticationFailed('No token provided')