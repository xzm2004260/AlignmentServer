'''
Created on 09/05/2018

@author: joro
'''
from rest_framework.test import APITestCase
import pytest
from django.contrib.auth.models import User
from django.urls.base import reverse
from rest_framework import status
from test.tests_server import PATH_TEST, GenericTestCase
import os
from Magixbackend.settings import MEDIA_ROOT
from alignment.thread_alignment import AlignThread
from alignment.models import Alignment


recording_URL = 'http://htftp.offroadsz.com/marinhaker/drugi/mp3/Soundtrack%20-%20Rocky/Rocky%20IV%20(1985)/01%20-%20Survivor%20-%20Burning%20Heart.mp3'


class UploadAudioTestCase(GenericTestCase):
    
    @pytest.mark.django_db
    def test_api_upload_audio(self):

        """Tests uploading audio to server.
            calls  AlignmentTestCase.setUp(self):
        """

        
        alignment_id = self.post_response.json()['alignment_id']
        data_upload = {
            'recording_url': recording_URL,
            'alignment_id': alignment_id
        }

        post_response = self.client.post(reverse('upload-audio'), data_upload) # upload audio
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        
        uploaded_recording_URI = os.path.join(MEDIA_ROOT, 'recordings/', str(alignment_id) + '.wav' )
        assert os.path.isfile(uploaded_recording_URI)   # check if file on server

#         alignment = Alignment.objects.get(id=alignment_id) 
#         self.assertEqual(alignment.status, 2) # check if on Queue. TODO: has to listen in a way for a save of object event. 
    
        
    def test_api_upload_wrong_id(self):

        """Tests uploading audio to non-existing alignment_id."""


        data_upload = {
            'recording_url': recording_URL,
            'alignment_id': -1
        }

        post_response = self.client.post(reverse('upload-audio'), data_upload) # upload audio
        self.assertEqual(post_response.status_code, status.HTTP_404_NOT_FOUND)



    def test_api_upload_not_complete_data(self):

        """Tests missing required fields."""

        self.not_complete_data_variants = [
            {
                'alignment_id': self.post_response.json()['alignment_id']
            },
            {
                'recording_url': recording_URL
            }
        ]

        for data in self.not_complete_data_variants:
            post_response = self.client.post(reverse('upload-audio'), data)
            self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)