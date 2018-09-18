'''
Created on 03/05/2018

@author: joro
'''

import threading
import logging
import os
import sys
import time


settings_name = os.environ.get('DJANGO_SETTINGS_MODULE')
if settings_name == 'config.settings.debug':
    from config.settings import debug as settings
elif settings_name == 'config.settings.production':
    from config.settings import production as settings

from alignment.models import Alignment, Status
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir,os.path.pardir ))
Alignment_dir = os.path.join(parentDir, 'AlignmentMagix')
if Alignment_dir not in sys.path:
    sys.path.append(Alignment_dir)


from src.align.doit import align_CMU
from src.align.ParametersAlgo import ParametersAlgo

 

class AlignThread (threading.Thread):
    def __init__(self, alignment_id, recording_URI ):
        threading.Thread.__init__(self)
        self.alignment_id = alignment_id
        self.recording_URI = recording_URI 
      


    def run(self):
        logging.info ("Starting alignment for alignment id " + str(self.alignment_id))
        
        alignment = Alignment.objects.get(id=self.alignment_id)
        alignment.status = Status.ONQUEUE # update status alignment
        alignment.save()
        composition_id = str(alignment.composition.id)
        
        #### set arguments 
        lyrics_URI = os.path.join(settings.MEDIA_ROOT, 'lyrics/', composition_id )
        output_URI = os.path.join(settings.MEDIA_ROOT, 'alignments/', self.alignment_id + '.lab.txt' )
        
        if not os.path.exists(self.recording_URI): # this should not happen
            sys.exit('file {} does not exist'.format(self.recording_URI) )
        
#         if not os.path.exists(output_URI): # align

        vocal_intervals_URI=None
        if alignment.level == 1: ### set level
            ParametersAlgo.DETECTION_TOKEN_LEVEL = 'words'
        elif alignment.level == 2:
            ParametersAlgo.DETECTION_TOKEN_LEVEL = 'lines'
        
        if alignment.accompaniment == 1: ### set accompaniment
            ParametersAlgo.POLYPHONIC = 0
        elif alignment.accompaniment == 2:
            ParametersAlgo.POLYPHONIC = 1

        try:
            detected_word_list =  align_CMU(self.recording_URI, lyrics_URI, output_URI, ParametersAlgo.WITH_SECTION_ANNO, vocal_intervals_URI ) #  align
            if ParametersAlgo.WITH_SECTION_ANNO == 0:
                detected_word_list = detected_word_list[0] # one section only
            
            alignment.timestamps  = convert_to_list(detected_word_list)
            
            alignment.error_reason = None
            alignment.status = Status.DONE # update status alignment
        except (RuntimeError, FileNotFoundError, NotImplementedError) as error:
            print(error)
            alignment.status = Status.FAILED
            alignment.error_reason = str(error)
            alignment.timestamps = None
#         time.sleep(3); detected_word_list = [ [[['word1',0,2]],[['word2',2,3]]] ]
                
        alignment.save()
        logging.info ("Finishing alignment for alignment id  " + str(self.alignment_id))


def convert_to_list(detected_word_list):
    '''convert list of DectedToken to easily parsable objects'''
    
    word_list_with_timestamps = []
    for detected_token in detected_word_list:
        token_as_list = detected_token.to_list()
        word_list_with_timestamps.append(token_as_list)
    
    word_list_with_timestamps_str = str(word_list_with_timestamps)
    return word_list_with_timestamps_str
