'''
Created on Dec 8, 2017

@author: joro
'''
import os
import sys
import logging
import numpy as np

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

testDir = os.path.dirname(os.path.realpath(__file__))


from src.align.ParametersAlgo import ParametersAlgo
from src.align.doit import align_CMU

from test.test_decoded_path_to_tokens import prepare_detected_and_reference_data
from test.test_load_lyrics import setUp_test_lyrics_input, test_load_lyrics


# setting both to 0 means default (English)
ParametersAlgo.FOR_MAKAM = 0
ParametersAlgo.FOR_JINGJU = 0

# test with section links. polyphonic

#     # test of audio working 
ParametersAlgo.WITH_ORACLE_ONSETS = -1
ParametersAlgo.WITH_ORACLE_PHONEMES = 0
# set WITH_DURATIONS in ParametersAlgo. it cannot be set here


######### essentially the alignent whole logic (all step-wise tests one after each other)

def test_lyrics_align():
    '''
    test alignment on word-level or phoneme-level 
    '''
    ParametersAlgo.WRITE_TO_FILE = 1 
    ParametersAlgo.DETECTION_TOKEN_LEVEL = 'words'
#     ParametersAlgo.DETECTION_TOKEN_LEVEL = 'phonemes' # designed and tested only for with_section_annotations=0 
    ParametersAlgo.LOGGING_LEVEL = logging.WARNING # avoid skipping alignment because of already aligned output file 
    for ParametersAlgo.POLYPHONIC in [0,1]: 
        for with_section_annotations in [2]: # TODO prepare polyphonic tests for rest of cases
            audioFileURI, lyrics_URI = setUp_test_lyrics_input(with_section_annotations, with_shortest_audio=True)
    
            vocal_intervals_URI = None
            output_URI = 'dummy'
            
            try:
                aligned_token_list = align_CMU(audioFileURI, lyrics_URI,  output_URI, with_section_annotations, vocal_intervals_URI, is_test_case=True)
            except (RuntimeError,FileNotFoundError, NotImplementedError) as error:
                logging.error(error)
                assert 0
        
            assert aligned_token_list is not None 
            assert type(aligned_token_list[0]) != str # if error occurs, the output is not tokens but a string error msg
            ref_start_times, detected_start_times, ref_tokens, deteceted_tokens = prepare_detected_and_reference_data(aligned_token_list, ParametersAlgo.DETECTION_TOKEN_LEVEL, with_section_annotations )
    
#         os.remove(output_URI)
            assert np.allclose(ref_start_times, detected_start_times, atol=1e-03)
            assert  ref_tokens == deteceted_tokens


    
if __name__ == '__main__':
    
#     test_align_line_level()
    test_lyrics_align()    


#     lyrics_URI = 'example/umbrella_lyrics_chorus.txt'
#     lyrics_URI = 'example/umbrella_line.txt'
#     lyrics_URI = 'example/umbrella_3lines.txt'
#     lyrics_URI = 'example/timed_lyrics.txt'


#     sectionLinksSourceURI =  'example/umbrella_1section_aligned.txt'     
#     audioFileURI = 'example/vignesh.wav'
#     audioFileURI = 'example/umbrella_line.wav'
#     audioFileURI = 'example//umbrella.wav'