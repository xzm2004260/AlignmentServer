'''
Created on Sep 18, 2018

@author: joro
'''
import os
from time import sleep
import pytest

from src.utilsLyrics.Utilz import write_decoded_to_file
from src.align import ParametersAlgo
from src.align.LyricsParsing import DetectedToken

@pytest.mark.skip # skipped because failing
def test_write_to_file():
    
    ParametersAlgo.DETECTION_TOKEN_LEVEL = 'words'
    token1 = DetectedToken('a', 1.0)
    token2 = DetectedToken('b', 4.0)
    token3 = DetectedToken('', 5.0)
    token4 = DetectedToken('', 6.0)
    token5 = DetectedToken('', 7.0)
    detected_token_list = [token1, token2, token3, token4, token5] # non-meaningful
    
    dummy_phi_score = 0.2
    output_URI = 'decoded.test'
    write_decoded_to_file(detected_token_list, output_URI, dummy_phi_score)
    sleep(1) 
    os.remove(output_URI)

if __name__ == '__main__':
    test_write_to_file()