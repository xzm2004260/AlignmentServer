from rest_framework import serializers
from django.contrib.auth.models import User
from services.jwt_helper import JWTHelper


class UserSignInSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'token']
        extra_kwargs = {'password': {'write_only': True}}

    def get_token(self, user):
        user = JWTHelper.encode_token(user)
        return user
