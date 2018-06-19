'''
Created on Dec 8, 2017

@author: joro
'''
import sys
import numpy as np
import os

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

from src.align.ParametersAlgo import ParametersAlgo
from src.align.doit import EXPECTED_ORDER

from src.utilsLyrics.Utilz import tsToFrameNumber
from src.align.LyricsAligner import LyricsAligner
from test.test_load_lyrics import setUp_recording

testDir = os.path.dirname(os.path.realpath(__file__))

ParametersAlgo.FOR_MAKAM = 0
ParametersAlgo.FOR_JINGJU = 0

def test_b_map():
    '''
    test extraction of observation probability matrix b-map with model
    '''
    
    ParametersAlgo.POLYPHONIC = 0
    recording = setUp_recording(with_section_annotations=0) # load umbrella-line
    
    la = LyricsAligner(recording, EXPECTED_ORDER, ParametersAlgo.PATH_TO_HCOPY)
    _, decoders, _ = la.alignRecording()
    
    assert len(decoders) > 0 # sanity prerequisite
    decoder = decoders[0]
    
    reference_b_map_URI = os.path.join(testDir,'persistent/B_map_umbrella_line.txt')
#     np.savetxt(reference_b_map_URI , decoder.hmmNetwork.B_map ) 

    B_map_reference = np.loadtxt(reference_b_map_URI) # stored in log domain

#     assert areArraysEqual ( decoder.hmmNetwork.B_map, B_map_reference)
    assert np.allclose(decoder. hmmNetwork.B_map, B_map_reference, atol=1e-03)
    

def test_b_map_non_vocal():
    '''
    assure in the b_map the hard-assignment of non-vocal probabilities  make sense 
    Test done for only with_section_annotations = 0, because checking only the decoder 0 corresponding to first section
    '''
    ParametersAlgo.POLYPHONIC = 0

    with_section_annotations = 0
    recording = setUp_recording(with_section_annotations, with_shortest_audio=False)
    
    vocal_intervals_URI = os.path.join(testDir, 'example/talkin_in_my_sleep_segs.txt') # modified so that it has non-vocal in time interval [14,15]
    recording.vocal_intervals_to_section_links(vocal_intervals_URI) 
    
    la = LyricsAligner(recording, EXPECTED_ORDER, ParametersAlgo.PATH_TO_HCOPY)
    _, decoders, _ = la.alignRecording()
    
    assert len(decoders) > 0
    decoder = decoders[0]
    assert len(decoder.hmmNetwork.list_non_vocal_intervals) > 0
    startFrame = tsToFrameNumber(decoder.hmmNetwork.list_non_vocal_intervals[0][0])
    endFrame = tsToFrameNumber(decoder.hmmNetwork.list_non_vocal_intervals[0][1])
  
    #### check hard threshold: set obs.prob of non-vocal states to 1, the rest to zero.  
    reference_b_map_non_vocal_URI = os.path.join( testDir,'persistent/B_map_non_vocal_segment_talking.txt')
#     np.savetxt(reference_b_map_non_vocal_URI , decoder.hmmNetwork.B_map[:,startFrame:endFrame] ) 
    
    B_map_reference_non_vocal = np.loadtxt(reference_b_map_non_vocal_URI) # stored in log domain
    assert np.allclose( decoder.hmmNetwork.B_map[:,startFrame:endFrame], B_map_reference_non_vocal, atol=1e-03 )


    
# def test_sanity_feature_extraction():
#     '''
#     make sure the extracted mfcc features make sense
#     '''
#     pass   

    
if __name__ == '__main__':
    test_b_map()
    
