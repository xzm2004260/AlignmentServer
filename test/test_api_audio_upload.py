'''
Created on 09/05/2018

@author: joro
'''
from rest_framework.test import APITestCase
import pytest
from django.contrib.auth.models import User
from django.urls.base import reverse
from rest_framework import status

from test.test_api_post_alignment import PATH_TEST, GenericTestCase
import os

settings = os.environ.get('DJANGO_SETTINGS_MODULE')

if settings == 'config.settings.test':
    from config.settings.test import MEDIA_ROOT
if settings == 'config.settings.production':
    from config.settings.production import MEDIA_ROOT
    
recording_URL = 'http://htftp.offroadsz.com/marinhaker/drugi/mp3/Soundtrack%20-%20Rocky/Rocky%20IV%20(1985)/01%20-%20Survivor%20-%20Burning%20Heart.mp3'
# recording_URL = os.path.join(MEDIA_ROOT, 'recordings/umbrella_line.mp3' )

# signed url. expired
signed_recording_URL = 'https://flowra-audio-recordings.s3.amazonaws.com/5b23e1cf6ba8f0282d19039c.mp3?AWSAccessKeyId=AKIAIOV6UBGWVLCNHMNA&Expires=1529087597&Signature=TrZ5Whn4iHF9mFpaO56f%2BYwQGgk%3D'

wrong_recording_URL = 'https://flowra-audio-recordings.s3.amazonaws.com/5b23e1cf6ba8f0282d19039c.mp'

class UploadAudioTestCase(GenericTestCase):
    
    @pytest.mark.django_db
    def test_api_upload_audio(self):

        """Tests uploading audio to server.
            calls  AlignmentTestCase.setUp(self):
        """

        post_response = self.client.post(reverse('create-alignment'), self.alignment_data_variants[0], format='multipart') # create one alignment object

        alignment_id = post_response.json()['alignment_id']
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

    
    def test_api_upload_wrong_url(self):

        """Tests uploading audio to url that does not indicate the URL type."""

        post_response = self.client.post(reverse('create-alignment'), self.alignment_data_variants[1], format='json') # create one alignment object
        alignment_id = post_response.json()['alignment_id']

        upload_data_variants = [{
            'recording_url': wrong_recording_URL,
            'alignment_id': alignment_id
        },
        {
            'recording_url': signed_recording_URL,
            'alignment_id': alignment_id
        }              
        ]
        
        for data_upload in upload_data_variants:
            upload_response = self.client.post(reverse('upload-audio'), data_upload) # upload audio
            self.assertEqual(upload_response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_api_upload_not_complete_data(self):

        """Tests missing required fields."""
        
        post_response = self.client.post(reverse('create-alignment'), self.alignment_data_variants[0], format='multipart') # create one alignment object

        self.not_complete_data_variants = [
            {
                'alignment_id': post_response.json()['alignment_id']
            },
            {
                'recording_url': recording_URL
            }
        ]

        for data in self.not_complete_data_variants:
            post_response = self.client.post(reverse('upload-audio'), data)
            self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)