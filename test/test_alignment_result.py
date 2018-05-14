'''
Created on 10/05/2018

@author: joro
'''
import pytest
from alignment.thread_alignment import AlignThread
from alignment.models import Alignment
import os
from test.test_post_alignment import GenericTestCase

testDir = os.path.dirname(os.path.realpath(__file__))

test_recording_URL = os.path.join(testDir,'data/umbrella_line.wav')


class AlignmentResultTestCase(GenericTestCase):

    @pytest.mark.django_db
    def ftest_api_timestamps_exist(self):
        '''
        Tests that on running the alignment algorithm the format of the result timestamps makes sense
        stub for uploading audio (using test audio recording)
        '''
        
        alignment_id = self.post_response.json()['alignment_id']
        
        ### run alignment with given test audio
        align_thread = AlignThread(alignment_id, test_recording_URL) 
        align_thread.start()
        align_thread.join() # wait for alignment to finish
        
        alignment = Alignment.objects.get(id=alignment_id) 
        self.assertEqual(alignment.status, 3) # check if status is DONE
        assert alignment.timestamps != 'null'
        
if __name__ == '__main__':
    a = AlignmentResultTestCase()
    a.test_api_timestamps_exist()        