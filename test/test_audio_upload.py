'''
Created on 09/05/2018

@author: joro
'''
from rest_framework.test import APITestCase
import pytest
from django.contrib.auth.models import User
from django.urls.base import reverse
from rest_framework import status
from test.tests_server import PATH_TEST
import os
from Magixbackend.settings import MEDIA_ROOT
from alignment.thread_alignment import AlignThread
from alignment.models import Alignment


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
        
        alignment_id = self.response.json()['alignment_id']
        data_upload = {
            'recording_url': recording_url,
            'alignment_id': alignment_id
        }

        post_response = self.client.post(reverse('upload-audio'), data_upload) # upload audio
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        
        audioFile_URI = os.path.join(MEDIA_ROOT, 'recordings/', str(alignment_id) + '.mp3' )
        assert os.path.isfile(audioFile_URI)   # check if file on server


#         alignment = Alignment.objects.get(id=alignment_id) 
#         self.assertEqual(alignment.status, 2) # check if on Queue. TODO: has to listen in a way for a save of object event. 
    
    def test_api_timestamps_exist(self):
        '''
        Tests that on running the alignment algorithm the format of the result timestamps makes sense 
        '''
        
        alignment_id = self.response.json()['alignment_id']
        ### run alignment with given test audio 1.wav 
        align_thread = AlignThread(alignment_id) 
        align_thread.start()
        align_thread.join() # wait for alignment to finish
        
        alignment = Alignment.objects.get(id=alignment_id) 
        self.assertEqual(alignment.status, 3) # check if status is done
        
         
    
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