# -*- coding: utf-8 -*-

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

#### the contents of example/umbrella_3lines.txt hhas to be the same as TEST_LYRICS
TEST_LYRICS_FILE_URI = os.path.join(PATH_TEST, 'example/umbrella_3lines.txt')
TEST_LYRICS = "because when the sun shines we shine together\ntold you i'll be here forever\nsaid i'll always be your friend"


settings_name = os.environ.get('DJANGO_SETTINGS_MODULE')


if settings_name == 'config.settings.test':
    from config.settings import test as settings
elif settings_name == 'config.settings.production':
    from config.settings import production as settings

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
        response = self.client.post(reverse('token'), password_data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertTrue('token' in response.data)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        self.f = open(TEST_LYRICS_FILE_URI, 'r')
        
        self.content_types = ['multipart','json'] # the first alignment_data_variants needs multipart because of the file
        self.alignment_data_variants = [
        {
            'title': 'new composition',
            'accompaniment': 1,
            'lyrics_file': self.f
 
         }
        ,
        {
           'title': 'new composition',
           'accompaniment': 1,
#            'lyrics_text': 'line1\nlinw2\nline3'
           'lyrics_text': TEST_LYRICS
        }
         ]
        
        self.not_complete_data_variants = [
        {
            'lyrics_file': self.f
        },
        {
            'lyrics_text': TEST_LYRICS
        },
        {
            'accompaniment': 2
        },
        {
            'composition_id':1
        }
        ]
        


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
        

        
   
    @pytest.mark.django_db
    def test_api_post_alignment(self):
        """
        Test the api has alignment creation capability. 
        THe number of compositions and alignments has to increase by one on correct alignment post
        Checks two cases: lyrics (as string) and lyrics_file
        Command: pytest alignment/tests

        """
        for i, alignment_data in enumerate(self.alignment_data_variants ):
            
            pre_post_count_aligns = Alignment.objects.count()
            pre_post_count_compositions = Composition.objects.count()
            post_response = self.client.post(reverse('create-alignment'), alignment_data, format=self.content_types[i]) # create one alignment object
    
    
            self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
            
            ### assert composition in  response
            self.assertIn('composition_id', post_response.data)

            ##### assert lyrics are fine
            comp_id = post_response.data['composition_id']
            composition = Composition.objects.get(id=comp_id)
            self.assertIn(settings.MEDIA_ROOT, composition.lyrics.path)
            lyrics_lines = composition.lyrics.readlines() # the content of the saved lyrics text file
            check_lyrics(lyrics_lines)
            
            #### assert 1 alignment object created
            self.assertIn('alignment_id', post_response.data)
            num_aligns_added = Alignment.objects.count() - pre_post_count_aligns
            self.assertEqual(num_aligns_added, 1)   
            
            #### assert 1 composition object created
            num_compositions_added = Composition.objects.count() - pre_post_count_compositions
            self.assertEqual(num_compositions_added, 1)

    @pytest.mark.django_db
    def test_api_post_alignment_by_comp_id(self):
        """
        Command:
        pytest alignment/tests

        """
        post_response = self.client.post(reverse('create-alignment'), self.alignment_data_variants[0], format='multipart') # create one alignment object

        pre_post_count_aligns = Alignment.objects.count()
        pre_post_count_compositions = Composition.objects.count()


        self.assertEqual(Composition.objects.count(), 1)

        comp_id = post_response.data['composition_id']
#         composition = Composition.objects.get(id=comp_id)
        
        alignment_data = {
            'title': 'test title 2',
            'accompaniment': 2,
            'level': 1,
            'composition_id': comp_id
         }
        post_response = self.client.post(reverse('create-alignment'), alignment_data) # create one alignment object
        num_aligns_added = Alignment.objects.count() - pre_post_count_aligns
        num_compositions_added = Composition.objects.count() - pre_post_count_compositions

        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(num_aligns_added, 1)
        self.assertEqual(num_compositions_added, 0)

    def test_not_complete_data(self):
        """Tests missing required fields."""


        for not_complete_data in self.not_complete_data_variants:
            post_response = self.client.post(reverse('create-alignment'), not_complete_data, format='multipart') # create one alignment object
            self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)

    
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
        post_response = self.client.post(reverse('create-alignment'), self.alignment_data_variants[0]) # create one alignment object

        alignment_id = post_response.data['alignment_id']
        alignment = Alignment.objects.get(id=alignment_id) # assume that there the first alignment object has id=1 
        response_from_get = self.client.get(
            reverse('alignment-detail', kwargs={'pk': alignment.pk}),
            format='json'
        )
        
        self.assertEqual(response_from_get.status_code, status.HTTP_200_OK)
        alignment_object = response_from_get.json()
        self.assertEqual(len(alignment_object), 8) # an alignment object has 8 fields
        self.assertEqual(alignment_object['level'], 1) # an alignment level is set by defaul to 1 (=Words)
        self.assertEqual(alignment_object['status'], 1) # an alignment status is set by defaul to 1 (=Not started)

def check_lyrics(lyrics_lines):
    '''
    compares given input to the reference TEST_LYRICS_FILE_URI
    '''
    with open(TEST_LYRICS_FILE_URI) as f:
        reference_lines = f.readlines()
    assert len(lyrics_lines) == len(reference_lines)
    for i,line in enumerate(lyrics_lines):
        line = line.decode('latin-1')
        assert line.strip() == reference_lines[i].strip()
