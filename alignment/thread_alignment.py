'''
Created on 03/05/2018

@author: joro
'''

import threading
import logging
import os

# from src.align.doit import align_CMU
from Magixbackend.settings import MEDIA_ROOT
from alignment.models import Alignment, Status
from src.align.doit import align_CMU
import sys
import time

 

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
        composition_id = alignment.composition.id.hex
        
        #### set arguments 
        lyrics_URI = os.path.join(MEDIA_ROOT, 'lyrics/', composition_id )
        output_URI = os.path.join(MEDIA_ROOT, 'alignments/', self.alignment_id + '.lab.txt' )
        
        if not os.path.exists(self.recording_URI):
            sys.exit('file {} does not exist'.format(self.recording_URI) )
        
#         if not os.path.exists(output_URI): # align

        with_section_anno=0
        vocal_intervals_URI=None
        detected_word_list =  align_CMU(self.recording_URI, lyrics_URI, output_URI, with_section_anno, vocal_intervals_URI ) #  align
        detected_word_list = detected_word_list[0] # one section only
        time.sleep(3); detected_word_list = [ [[['word1',0,2]],[['word2',2,3]]] ]
                
#         with open(output_URI, 'r') as f1:
#                 detectedTokenList = json.load( f1) 
        alignment.timestamps = str(detected_word_list)
        alignment.status = Status.DONE # update status alignment
        alignment.save()
        logging.info ("Finishing alignment for alignment id  " + str(self.alignment_id))

