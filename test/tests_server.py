import os
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
import pytest
from rest_framework.test import APIClient
from alignment.models import Alignment
from composition.models import Composition
from django.contrib.auth.models import User
from Magixbackend.settings import MEDIA_ROOT

PATH_TEST = os.path.dirname(os.path.realpath(__file__)) 


class GenericTestCase(APITestCase):
    """
    Test suite for the api views.
    
    """
    @pytest.mark.django_db
    def setUp(self):
        """Setup authentication and alignment creation."""

        user = User.objects.create_user(username='mirza', email='mirza@gmail.com', password='old_pass')
        user.is_active = True
        user.save()
        password_data = {
            'username': 'mirza',
            'password': 'old_pass'
        }

        # response = self.client.post(reverse('password-change'), change_password_data, format='json')

        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(reverse('signin'), password_data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertTrue('token' in response.data)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        self.f = open(os.path.join(PATH_TEST, 'data/umbrella_line.txt'), 'r')
        
        self.alignment_data = {
            'title': 'new composition',
            'accompaniment': 2,
            'lyrics': self.f
         }

        self.pre_post_count_aligns = Alignment.objects.count()
        self.pre_post_count_compositions = Composition.objects.count()
        
        self.post_response = self.client.post(reverse('create-alignment'), self.alignment_data, format='multipart') # create one alignment object




class PostAlignmentTestCase(GenericTestCase):
    """
    Test suite for the api views.

    """
    @pytest.mark.django_db
    def setUp(self):
        GenericTestCase.setUp(self)
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

        alignment = Alignment.objects.get(id=1) # assume that there the first alignment object has id=1 
        response_from_get = self.client.get(
            reverse('alignment-detail', kwargs={'pk': alignment.pk}),
            format='json'
        )
        
        self.assertEqual(response_from_get.status_code, status.HTTP_200_OK)
        alignment_object = response_from_get.json()
        self.assertEqual(len(alignment_object), 7) # an alignment object has 7 fields
        self.assertEqual(alignment_object['level'], 1) # an alignment level is set by defaul to 1 (=Words)
        self.assertEqual(alignment_object['status'], 1) # an alignment status is set by defaul to 1 (=Not started)





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
