from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
import pytest


class Authentication(APITestCase):
    """
    Test suite for change password and and sign in.
    """

    @pytest.mark.django_db
    def test_api_change_password_and_sign_in(self):
        user = User.objects.create_user(username='mirza', email='mirza@gmail.com', password='old_pass')
        user.is_active = False
        user.save()
        self.change_password_data = {
            'username': 'mirza',
            'password': 'new_pass'
        }

        response = self.client.post(reverse('password-change'), self.change_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(reverse('signin'), self.change_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)


