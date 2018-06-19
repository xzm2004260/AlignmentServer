'''
Created on Jan 25, 2018

@author: joro
'''
import numpy as np
import os

from src.align.GenericRecording import GenericRecording,\
    extract_non_vocal_in_interval

testDir = os.path.dirname(os.path.realpath(__file__))

def test_non_vocal_intervals():
    '''
    loading of non-vocal intervals, check sanity of derived intervals
    '''
    audioFileURI = os.path.join(testDir, 'example/umbrella_line.wav')
    vocal_intervals_URI = os.path.join(testDir,'example/umbrella_line_vocal_segs.txt')  # one vocal interval starting after second 0 and ending before end of audio
    
    recording = GenericRecording(audioFileURI)
    
    vocal_intervals, non_vocal_intervals =  recording._load_vocal_intervals(vocal_intervals_URI)
    ### assert that there is a non_vocal created at beginning and end
    assert non_vocal_intervals[0][1] == vocal_intervals[0][0] 
    assert vocal_intervals[-1][1] < recording.duration
    assert non_vocal_intervals[-1][1] ==  recording.duration
    


def test_extract_vocal_intervals():
    '''
    extract non-vocal intervals in a specified interval
    '''
    
    input_intervals = np.array([[5, 10],[15,20],[23,30]])
#     input_intervals = np.array([])
    
    est_intervals = extract_non_vocal_in_interval(input_intervals, 2, 17) # specified interval
    assert np.allclose(est_intervals, np.array([[ 5,10],[15,17]]) )

if __name__ == '__main__':
    test_extract_vocal_intervals()