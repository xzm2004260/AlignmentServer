'''
Created on Feb 16, 2018

@author: joro
'''
import os
import sys
from test.test_load_lyrics import setUp_recording
from src.align.ParametersAlgo import ParametersAlgo
import scipy.io.wavfile

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

testDir = os.path.dirname(os.path.realpath(__file__))


ParametersAlgo.FOR_MAKAM = 0
ParametersAlgo.FOR_JINGJU = 0
ParametersAlgo.POLYPHONIC = 1




def test_separate():
    '''
    test source separation works
    '''

#     for ParametersAlgo.DETECTION_TOKEN_LEVEL in ['lines', 'phonemes', 'words']:
    
    with_section_annotations = 0 # no persistent tokens for phonemes in other test  cases prepared
    
    ### prepare lyrics of recording. do not change input, run_backtrack hard coded to work with umbrella_line
    recording = setUp_recording(with_section_annotations, with_shortest_audio=True)
    section_link = recording.sectionLinks[0]
    audio_segment = section_link.get_audio_segment(recording.audio, recording.sample_rate)
    audio_segment_separated = recording.sectionLinks[0].separate_vocal(audio_segment, recording.sample_rate)
    
    assert audio_segment_separated is not None
    audio = audio_segment_separated.astype('int16')
    scipy.io.wavfile.write(filename='/Users/joro/Downloads/test.wav', rate=recording.sample_rate, data=audio) # write back to file, because htk needs to read a file


if __name__ == '__main__':
    test_separate()