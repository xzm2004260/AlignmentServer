'''
Created on Jan 22, 2018

@author: joro
'''
import os
import sys
import json
import logging
import numpy as np


projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)
testDir = os.path.dirname(os.path.realpath(__file__))
    
from src.utilsLyrics.UtilsLyricsParsing import load_section_annotations
from src.align.doit import create_recording
from src.align.ParametersAlgo import ParametersAlgo


    # setting both to 0 means default (English)
ParametersAlgo.FOR_MAKAM = 0
ParametersAlgo.FOR_JINGJU = 0

ParametersAlgo.POLYPHONIC = 0
    # set WITH_DURATIONS in ParametersAlgo. it cannot be set here
#     lyrics_URI =  os.path.join(testDir, 'example/lyrics_with_spanish.txt')

def setUp_test_lyrics_input(with_section_annotations, with_shortest_audio=True):
    '''
    helper: load the corresponding txt file
    with_shortets_audio: use short audio excerpt for faster completion of all tests. useful in some cases 
    '''
    audioFileURI = os.path.join(testDir, 'example/talkin_in_my_sleep.wav')
    
    if with_section_annotations == 0:
        if with_shortest_audio:
            #### this data has  shorter processing time. input data for assert for this case
            lyrics_filename = 'example/umbrella_line.txt'
            if ParametersAlgo.DETECTION_TOKEN_LEVEL == 'lines':         # in test_decoded_path_to one can use with_shortest_audio=False. So we need to store the path for them. 
                lyrics_filename = 'example/umbrella_line_split.txt'
            audioFileURI = os.path.join(testDir, 'example/umbrella_line.wav')

#####  whole 4-minute recording
#         lyrics_filename = 'example/umbrella.txt'
#         audioFileURI = os.path.join(testDir, 'example/umbrella.wav')

        else:
            ##### 51-second excerpt.
            lyrics_filename = 'example/talkin_in_my_sleep.txt'

    elif with_section_annotations == 1:    
        lyrics_filename = 'example/talkin_in_my_sleep.sections.txt'
    elif with_section_annotations == 2:    
        lyrics_filename = 'example/talkin_in_my_sleep.timed_lines.lrc'
#         lyrics_filename = 'example/talkin_in_my_sleep.timed_lines.txt'
    lyrics_URI =  os.path.join(testDir, lyrics_filename)
#     lyrics_URI =  os.path.join(testDir, 'example/lyrics_with_spanish.txt')

    return audioFileURI, lyrics_URI

def setUp_recording(with_section_annotations, with_shortest_audio=True):
    '''
    helper 
    '''
    audioFileURI, lyrics_URI = setUp_test_lyrics_input(with_section_annotations, with_shortest_audio)
    recording = create_recording(audioFileURI, lyrics_URI, with_section_annotations, is_test_case=True) 
    return recording

def test_load_lyrics():
    '''
    test loading of lyrics form a .txt file, each lyric line is on a new line. no annotation timestamps
    tests if special characters and numbers are  handled ok 
    '''
    try:
        recording = setUp_recording(with_section_annotations=0, with_shortest_audio=False) # test made with longer audio lyrics
    except FileNotFoundError as e:
        logging.error(e)
        assert 0
# code for generating the reference test output    
#     lyrics_loaded_str = recording.sectionLinks[0].section.lyrics.__str__()
#     with open('persistent/talkin_in_my_sleep.lyrics_str.json', 'w') as f:
#         json.dump(lyrics_loaded_str, f ) 
    
    # load from persistent
    URI_persistent_path = os.path.join(testDir, 'persistent/talkin_in_my_sleep.lyrics_str.json')
    with open(URI_persistent_path, 'r') as f:
        persistent_lyrics = json.load(f)
    lyrics = recording.sectionLinks[0].section.lyrics.__str__()
    
    assert lyrics == persistent_lyrics  
    

def test_load_section_annotations():
    '''
    test the function to parse  lyrics .txt file that includes section timestamps 
    '''
    sectionLinksURI  = os.path.join(testDir,'example/talkin_in_my_sleep.sections.txt')
    begin_timestamps, section_lyrics = load_section_annotations(sectionLinksURI)
    assert begin_timestamps == [13.310417, 21.669792, 29.710417, 46.180208]
    assert section_lyrics == ["Talkin' in my sleep at night,\nMakin' myself crazy\n(Out of my mind, out of my mind)", "Wrote it down and read it out,\nHopin' it would save me\n(Too many times, too many times)", "My love, he makes me feel\nlike nobody else, nobody else\nBut my love, he doesn't love me,\nso I tell myself, I tell myself", "One, don't pick up the phone\nYou know he's only calling\n'cause he's drunk and alone two"]

#     sectionLinksURI  = os.path.join(testDir,'example/shape_on_me.sections.txt') # this is not working on flowra's data because of the issue: 
#     sectionLinksURI = '/Users/joro/Documents/VOICE_magix/flowra/dataset/10-Drew_Tabor-Shape_on_me.txt'
#     begin_timestamps, section_lyrics = load_section_annotations(sectionLinksURI)
#     assert begin_timestamps == [10.4, 31.2] 

#     TODO: add here also test_load_lyrics_sections 


def test_load_lyrics_timed_lines():
    '''
    load lyrics as .txt file 
    '''
    recording = setUp_recording(with_section_annotations=2)
   
#     vocal_intervals_URI = os.path.join(testDir, 'example/talkin_in_my_sleep_segs.txt' ) # or vocal_intervals_URI = None
#     recording.vocal_intervals_to_section_links(vocal_intervals_URI) 
    
    # load from persistent
    URI_persistent_path = os.path.join(testDir, 'persistent/talkin_in_my_sleep.timed_lines.lyrics_str.json')
    with open(URI_persistent_path, 'r') as f:
        persistent_lyrics = json.load(f)
    
    all_begin_ts = []
    all_lyrics = []
    for section_link in  recording.sectionLinks:
        lyrics_loaded_str =  section_link.section.lyrics.__str__()
        all_lyrics.append(lyrics_loaded_str)
        all_begin_ts.append(section_link.beginTs)
    
    assert all_lyrics == persistent_lyrics
    
    reference_line_times = np.array([13.310417, 15.139583, 17.939583, 21.669792, 23.8, 25.880208, 29.710417, 32.789583, 37.139583, 40.930208, 46.180208, 48.4, 49.7])
    assert np.allclose(np.array(all_begin_ts), reference_line_times, atol=1e-03)

###### code for generating the reference test output    
#     all_lyrics = []
#     for section_link in  recording.sectionLinks:
#         lyrics_loaded_str =  section_link.section.lyrics.__str__()
#         all_lyrics.append(lyrics_loaded_str)
#         
#     with open('persistent/talkin_in_my_sleep.lines.lyrics_str.json', 'w') as f:
#         json.dump(all_lyrics, f ) 

if __name__ == '__main__':
#     test_load_lyrics()
    test_load_lyrics_timed_lines()
