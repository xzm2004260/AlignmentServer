'''
Created on Feb 1, 2018

@author: joro
'''
import os
import sys
from src.align.LyricsParsing import DetectedToken

testDir = os.path.dirname(os.path.realpath(__file__))

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)


from src.align.ParametersAlgo import ParametersAlgo
from src.align.LyricsAligner import fix_non_meaningful_timestamps


def test_fix_time_intervals():
    """test that non-meaningful intervals in alignment results are fixed"""
    
    # setup input data
    ParametersAlgo.DETECTION_TOKEN_LEVEL = 'words'
    token1 = DetectedToken('a', 1.0)
    token2 = DetectedToken('b', 4.0)
    token3 = DetectedToken('.', 5.0)
    existing_token_list = [token1, token2, token3] # non-meaningful
    
    token4 = DetectedToken('c', 2.0)
    incoming_token_list = [token4] 

    modified_existing_token_list = fix_non_meaningful_timestamps(existing_token_list, incoming_token_list) # call
    modif_list = [] ##### needed for comparison
    for token in modified_existing_token_list:
        modif_list.append(token.to_list() )
    
    # setup reference
    token5 = DetectedToken('b', 1.33)
    token6 = DetectedToken('.', 1.67)    
    reference_token_list = [token1, token5, token6]
    ref_list = [] ##### needed for comparison
    for token in reference_token_list:
        ref_list.append(token.to_list())
        
        
    assert ref_list == modif_list

if __name__ == '__main__':
    test_fix_time_intervals()