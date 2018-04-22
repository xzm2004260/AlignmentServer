import io
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
import pytest
from urllib import parse
from alignment.models import Alignment
from composition.models import Composition


class AlignmentTestCase(APITestCase):
    """
    Test suite for the api views.

    """

    @pytest.mark.django_db
    def setUp(self):
        
        f = open('test_data/test_file.txt', 'r')
        self.alignment_data = {
            'title': 'new composition',
            'accompaniment': 2,
            'level': 1,
            'lyrics': f
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

        self.assertIn('lyrics_id', self.post_response.data)
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
        # print(self.post_response.json() )
        num_aligns_added = Alignment.objects.count() - pre_post_count_aligns
        num_compositions_added = Composition.objects.count() - pre_post_count_compositions
        
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(num_aligns_added, 1)
        self.assertEqual(num_compositions_added, 0)
        

    @pytest.mark.django_db
    def test_api_post_alignment_wrong_id(self):

        post_response = self.client.post(reverse('create-alignment'), self.alignment_data_by_comp_id) # create one alignment object

        self.assertEqual(post_response.status_code, status.HTTP_404_NOT_FOUND)        

    @pytest.mark.django_db
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
        self.assertEqual(len(response.json()), 6) # an alignment object has 6 fields
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UploadAudioTestCase(APITestCase):

    @pytest.mark.django_db
    def setUp(self):
        atc = AlignmentTestCase() 

    # calls  AlignmentTestCase.setUp(self):
    def test_api_upload_audio(self):
        '''
        tests uploading audio to server
        '''
        recording_URL = 'http://htftp.offroadsz.com/marinhaker/drugi/mp3/Soundtrack%20-%20Rocky/Rocky%20IV%20(1985)/01%20-%20Survivor%20-%20Burning%20Heart.mp3'

        data_upload = {
        'recording_URL' : recording_URL,
        'alignment_id': 1
        }

        post_response = self.client.post(reverse('upload-audio'), data_upload) # upload audio
        self.assertEqual(post_response.status_code, status.HTTP_200_OK)
        # check if file on server

    # # calls  AlignmentTestCase.setUp(self):
    # def test_api_upload_wrong(self):
    #     '''
    #     tests uploading audio to non-existing alignment_id
    #     '''
    #     recording_URL = 'http://htftp.offroadsz.com/marinhaker/drugi/mp3/Soundtrack%20-%20Rocky/Rocky%20IV%20(1985)/01%20-%20Survivor%20-%20Burning%20Heart.mp3'

    #     data_upload = {
    #     'recording_URL' : recording_URL,
    #     'alignment_id': -1
    #     }

    #     post_response = self.client.post(reverse('upload-audio'), data_upload) # upload audio
    #     self.assertEqual(post_response.status_code, status.HTTP_404_NOT_FOUND)