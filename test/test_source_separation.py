'''
Created on Feb 16, 2018

@author: joro
'''
import os
import sys
from test.test_load_lyrics import setUp_recording
from src.align.ParametersAlgo import ParametersAlgo
import scipy.io.wavfile
from src.align.separate import separate
from src.align.FeatureExtractor import MODEL_PATH

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

    for ParametersAlgo.DETECTION_TOKEN_LEVEL in ['lines', 'phonemes', 'words']: # , 
    
        with_section_annotations= 0 # persistent tokens for phonemes prepared only for with_secion anno = 0
        
        ### prepare lyrics of recording. do not change input, run_backtrack hard coded to work with umbrella_line
        recording = setUp_recording(with_section_annotations, with_shortest_audio=True)
        section_link = recording.sectionLinks[0]
        audio_segment = section_link.get_audio_segment(recording.audio, recording.sample_rate)
        audio_segment_separated = recording.sectionLinks[0].separate_vocal(audio_segment, recording.sample_rate)
        file_name = 'test.wav'
        assert audio_segment_separated is not None
        audio = audio_segment_separated.astype('int16')
        scipy.io.wavfile.write(filename=file_name, rate=recording.sample_rate, data=audio) # write back to file, because htk needs to read a file
        os.remove(file_name)

def test_run_separation():
    audio_path = '/Users/joro/Documents/pandora+karoke_songs/taylor_swift_karaoke.wav'
    audio_path = '/Users/joro/Documents/pandora+karoke_songs/taylor_swift_original.wav'

    sample_rate, audio = scipy.io.wavfile.read(audio_path)
    model_URI = os.path.join(MODEL_PATH, 'krast.dad')
    audio_sep = separate(audio, model_URI, 0.3, 30, 25, 32, 513)
    scipy.io.wavfile.write(filename= '/Users/joro/Documents/pandora+karoke_songs/taylor_swift_original_vocal.wav', rate=sample_rate, data=audio_sep) # write back to file, because htk needs to read a file


if __name__ == '__main__':
#     test_separate()
    test_run_separation()