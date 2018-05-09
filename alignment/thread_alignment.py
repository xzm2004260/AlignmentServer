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
import json
import time

 

class AlignThread (threading.Thread):
    def __init__(self, alignment_id ):
        threading.Thread.__init__(self)
        self.alignment_id = alignment_id
      
    def run(self):
        logging.info ("Starting " + str(self.alignment_id))
        
        alignment = Alignment.objects.get(id=self.alignment_id)
        alignment.status = Status.ONQUEUE # update status alignment
        alignment.save()
        composition_id = alignment.composition.id.hex
        
        #### set arguments 
        audioFile_URI = os.path.join(MEDIA_ROOT, 'recordings/', self.alignment_id + '.mp3' )
        lyrics_URI = os.path.join(MEDIA_ROOT, 'lyrics/', composition_id )
        output_URI = os.path.join(MEDIA_ROOT, 'alignments/', self.alignment_id + '.lab.txt' )
        
#         if not os.path.exists(output_URI): # align
#     detected_word_list =  align_CMU(audioFile_URI, lyrics_URI, output_URI, with_section_anno=0, vocal_intervals_URI=None ) #  align
        time.sleep(3); detectedTokenList = [ [[['word1',0,2]],[['word2',2,3]]] ]
        detectedTokenList = detectedTokenList[0] # one section only
#             with open(output_URI, 'w') as f1:
#                 json.dump(detectedTokenList, f1) 
                
#         with open(output_URI, 'r') as f1:
#                 detectedTokenList = json.load( f1) 
        alignment.timestamps = str(detectedTokenList)
        alignment.status = Status.DONE # update status alignment
        alignment.save()
        logging.info ("Exiting " + str(self.alignment_id))

