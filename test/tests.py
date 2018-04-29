import io
import os
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
import pytest
from rest_framework.test import APIClient
from alignment.models import Alignment
from composition.models import Composition
from django.contrib.auth.models import User

PATH_TEST = os.path.dirname(os.path.realpath(__file__)) 


class AlignmentTestCase(APITestCase):
    """
    Test suite for the api views.

    """
    @pytest.mark.django_db
    def setUp(self):
        """Setup authentication and alignment creation."""

        user = User.objects.create_user(username='mirza', email='mirza@gmail.com', password='old_pass')
        user.is_active = False
        user.save()
        change_password_data = {
            'username': 'mirza',
            'password': 'new_pass'
        }

        response = self.client.post(reverse('password-change'), change_password_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(reverse('signin'), change_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.f = open(os.path.join(PATH_TEST, 'test_file.txt'), 'r')
        self.alignment_data = {
            'title': 'new composition',
            'accompaniment': 2,
            'lyrics': self.f
         }

        self.pre_post_count_aligns = Alignment.objects.count()
        self.pre_post_count_compositions = Composition.objects.count()
        self.post_response = self.client.post(reverse('create-alignment'), self.alignment_data, format='multipart') # create one alignment object

        self.alignment_data_by_comp_id = {
            'title': 'test title 2',
            'accompaniment': 2,
            'level': 1,
            'composition_id': -1
         }

    def test_not_complete_data(self):

        """Tests missing required fields."""

        not_complete_data_variants = [
        {
            'lyrics': self.f
        },
        {
            'accompaniment': 2
        },
        {
            'composition_id':1
        }
        ]
        for not_complete_data in not_complete_data_variants:
            post_response = self.client.post(reverse('create-alignment'), not_complete_data, format='multipart') # create one alignment object
            self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.django_db
    def test_api_post_alignment(self):
        """
        Test the api has alignment creation capability.

        Command:
        pytest alignment/tests

        """
        num_aligns_added = Alignment.objects.count() - self.pre_post_count_aligns
        num_compositions_added = Composition.objects.count() - self.pre_post_count_compositions

        self.assertEqual(self.post_response.status_code, status.HTTP_201_CREATED)
        # self.assertTrue(parse(self.post_response.data['lyrics']).path.startswith(settings.MEDIA_URL))
        self.assertIn('alignment_id', self.post_response.data)
        self.assertEqual(num_aligns_added, 1)

        # self.assertIn('lyrics', self.post_response.data)
        self.assertEqual(num_compositions_added, 1)

    @pytest.mark.django_db
    def test_api_post_alignment_by_comp_id(self):
        """
        Command:
        pytest alignment/tests

        """

        pre_post_count_aligns = Alignment.objects.count()
        pre_post_count_compositions = Composition.objects.count()

        query_set = Composition.objects.filter(title=self.alignment_data['title']) # get the just uploaded composition

        self.assertEqual(Composition.objects.count(), 1)

        composition = query_set[0] # there is only one composition with this name

        comp_id = composition.id
        alignment_data_by_comp_id = {
            'title': 'test title 2',
            'accompaniment': 2,
            'level': 1,
            'composition_id': comp_id
         }
        post_response = self.client.post(reverse('create-alignment'), alignment_data_by_comp_id) # create one alignment object
        num_aligns_added = Alignment.objects.count() - pre_post_count_aligns
        num_compositions_added = Composition.objects.count() - pre_post_count_compositions

        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(num_aligns_added, 1)
        self.assertEqual(num_compositions_added, 0)

    @pytest.mark.django_db
    def test_api_post_alignment_wrong_id(self):
        post_response = self.client.post(reverse('create-alignment'), self.alignment_data_by_comp_id)
        self.assertEqual(post_response.status_code, status.HTTP_404_NOT_FOUND)

    @pytest.mark.django_db
    def test_api_post_alignment_wrong_token(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer mn432sjjkaoiherqwe')
        post_response = client.post(reverse('create-alignment'), self.alignment_data_by_comp_id)
        self.assertEqual(post_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_get_alignment(self):
        """
        Test the api to get an alignment.

        Command:
        pytest alignment/tests

        """
        self.post_response = self.client.post(reverse('create-alignment'), self.alignment_data) # create one alignment object

        align = Alignment.objects.get(id=1)
        response = self.client.get(
            reverse('alignment-detail', kwargs={'pk': align.pk}),
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()), 6) # an alignment object has 6 fields
        self.assertEqual(response.json()['level'], 1) # an alignment level is set by defaul to 1 (=Words)
        self.assertEqual(response.json()['status'], 1) # an alignment status is set by defaul to 1 (=Not started)


class UploadAudioTestCase(APITestCase):

    @pytest.mark.django_db
    def setUp(self):
        """Setup of authentication and alignment creation for uploading audio."""

        user = User.objects.create_user(username='mirza', email='mirza@gmail.com', password='old_pass')
        user.is_active = False
        user.save()
        change_password_data = {
            'username': 'mirza',
            'password': 'new_pass'
        }

        response = self.client.post(reverse('password-change'), change_password_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('signin'), change_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.f = open(os.path.join(PATH_TEST, 'test_file.txt'), 'r')

        self.alignment_data = {
            'title': 'new composition',
            'accompaniment': 2,
            'lyrics': self.f
        }

        self.response = self.client.post(reverse('create-alignment'), self.alignment_data)

    # calls  AlignmentTestCase.setUp(self):
    def test_api_upload_audio(self):

        """Tests uploading audio to server."""

        recording_url = 'http://htftp.offroadsz.com/marinhaker/drugi/mp3/Soundtrack%20-%20Rocky/Rocky%20IV%20(1985)/01%20-%20Survivor%20-%20Burning%20Heart.mp3'

        data_upload = {
            'recording_url': recording_url,
            'alignment_id': self.response.json()['alignment_id']
        }

        post_response = self.client.post(reverse('upload-audio'), data_upload) # upload audio
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        # check manually if file on server

    def test_api_upload_wrong_id(self):

        """Tests uploading audio to non-existing alignment_id."""

        recording_url = 'http://htftp.offroadsz.com/marinhaker/drugi/mp3/Soundtrack%20-%20Rocky/Rocky%20IV%20(1985)/01%20-%20Survivor%20-%20Burning%20Heart.mp3'

        data_upload = {
            'recording_url': recording_url,
            'alignment_id': -1
        }

        post_response = self.client.post(reverse('upload-audio'), data_upload) # upload audio
        self.assertEqual(post_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_upload_not_complete_data(self):

        """Tests missing required fields."""

        self.not_complete_data_variants = [
            {
                'alignment_id': self.response.json()['alignment_id']
            },
            {
                'recording_url': 'http://htftp.offroadsz.com/marinhaker/drugi/mp3/Soundtrack%20-%20Rocky/Rocky%20IV%20(1985)/01%20-%20Survivor%20-%20Burning%20Heart.mp3'
            }
        ]

        for data in self.not_complete_data_variants:
            post_response = self.client.post(reverse('upload-audio'), data)
            self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)


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
