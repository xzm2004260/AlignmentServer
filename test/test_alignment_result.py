'''
Created on 10/05/2018

@author: joro
'''
import pytest
import os
import sys

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)
    
from alignment.thread_alignment import AlignThread
from alignment.models import Alignment
from test.test_post_alignment import GenericTestCase
from tl.testing.thread import ThreadJoiner

testDir = os.path.dirname(os.path.realpath(__file__))

test_recording_URL = os.path.join(testDir,'data/umbrella_line.wav')


# TODO: another test with very short audio, so that we can check error_reason != None and timestamps == None
class AlignmentResultTestCase(GenericTestCase):

    @pytest.mark.django_db
    def tes_api_timestamps_exist(self):
        '''
        Tests that on running the alignment algorithm the format of the result timestamps makes sense
        stub for uploading audio (using test audio recording)
        '''
        
        alignment_id = self.post_response.json()['alignment_id']
        
        with ThreadJoiner(100):
            ### run alignment with given test audio, skip uploading the audio by API method
            align_thread = AlignThread(alignment_id, test_recording_URL) 
            align_thread.start()
        
        alignment = Alignment.objects.get(id=alignment_id) 
        self.assertEqual(alignment.status, 3) # check if status is DONE
        assert alignment.timestamps != None
        # TODO: assert timestamps  is array
        assert alignment.error_reason == None
        
if __name__ == '__main__':
    a = AlignmentResultTestCase()
    a.test_api_timestamps_exist()        