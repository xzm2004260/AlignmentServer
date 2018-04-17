import io
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
import pytest

from .models import Alignment


class AlignmentTestCase(APITestCase):
    """
    Test suite for the api views.

    """

    @staticmethod
    def _create_test_file():
        return io.StringIO("this is a test file!")

    @pytest.mark.django_db
    def setUp(self):    
        self.alignment_data = {
            'title': 'test title 2',
            'accompaniment': 2,
            'level': 1,
            'lyrics': self._create_test_file()
         }
        self.post_response = self.client.post(reverse('create-alignment'), self.alignment_data)


    
    @pytest.mark.django_db
    def test_api_post_alignment(self):
        """
        Test the api has alignment creation capability.

        Command:
        pytest alignment/tests

        """

        print(self.post_response.json() )
        self.assertEqual(self.post_response.status_code, status.HTTP_200_OK)

    @pytest.mark.django_db
    def test_api_get_alignment(self):
        """
        Test the api to get an alignment.

        Command:
        pytest alignment/tests

        """

        align = Alignment.objects.get(id=1)
        response = self.client.get(
            reverse('alignment-detail', kwargs={'pk': align.pk}),
            format='json'
        )
        self.assertEqual(len(response.json()), 6) # an alignment object has 6 fields

        self.assertEqual(response.status_code, status.HTTP_200_OK)
