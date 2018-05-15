from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth import authenticate
from rest_framework import exceptions
from django.utils import timezone
from services.exceptions import UserDoesNotExistsException
from authentication.serializer import UserSignInSerializer


class ChangePasswordView(APIView):

    """
    View for changing password.

        POST: auth/password/change/signin

        Params:
        {
            "username": "mirza",
            "password": "newpassword123"
        }

    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        try:
            user = User.objects.get(username=username)
            if user and getattr(user, 'last_login', None) is None:
                user.set_password(password)
                user.is_active = True
                user.save()
                return Response("Password changed successfully.", status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise UserDoesNotExistsException()
        return Response("Token expired.", status=status.HTTP_400_BAD_REQUEST)


class UserSignInAPIView(APIView):

    """
    This view is used to login with new password.

        POST: auth/token

        Params:
        {
            "username": "mirza",
            "password": "newpassword123"
        }

    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        user = authenticate(username=username, password=password)
        if user and getattr(user, 'last_login', None) is None:
            user.last_login = timezone.now()
            user.save()
            serializer = UserSignInSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Invalid credentials or token already generated", status=status.HTTP_404_NOT_FOUND)


