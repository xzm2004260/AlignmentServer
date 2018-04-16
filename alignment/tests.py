import io
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Alignment


class AlignmentTestCase(APITestCase):
    """
    Test suite for the api views.

    """

    @staticmethod
    def _create_test_file():
        return io.StringIO("this is a test file!")

    def setUp(self):
        self.alignment_data = {
            'title': 'test title 2',
            'accompaniment': 2,
            'level': 1,
            'lyrics': self._create_test_file()
         }

        self.response = self.client.post(
            reverse('create-alignment'),
            self.alignment_data)

    def test_api_create_alignment(self):
        """
        Test the api has alignment creation capability.

        Command:
        python manage.py test alignment.tests.AlignmentTestCase.test_api_create_alignment

        """

        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_api_get_alignment(self):
        """
        Test the api to get an alignment.

        Command:
        python manage.py test alignment.tests.AlignmentTestCase.test_api_get_alignment


        """

        align = Alignment.objects.get(id=1)
        response = self.client.get(
            reverse('alignment-detail', kwargs={'pk': align.pk}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
