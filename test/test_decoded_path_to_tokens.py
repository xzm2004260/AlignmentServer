'''
Created on Feb 16, 2018

@author: joro
'''
import os
import sys

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

testDir = os.path.dirname(os.path.realpath(__file__))

from src.utilsLyrics.UtilsLyricsParsing import load_delimited
from src.utilsLyrics.UtilzNumpy import assertListsEqual
from src.hmm.Path import Path
from src.align.ParametersAlgo import ParametersAlgo
import json
from src.align.LyricsParsing import _constructTimeStampsForTokenDetected,\
    expand_path_to_wordList, expand_path_to_phonemes_list,\
    word_list_to_line_list
from src.align.LyricsAligner import LyricsAligner, is_detected_path_meaningful

from test.test_load_lyrics import setUp_recording

ParametersAlgo.FOR_MAKAM = 0
ParametersAlgo.FOR_JINGJU = 0
ParametersAlgo.POLYPHONIC = 0


   





def prepare_detected_and_reference_data(detectedTokenList, detection_token_level, with_section_annotations):
    '''
    helper method to load test data
    
    Parameters:
    -----
    assumes that detected_token list has the tokens grouped in highest level array of sections
    
    '''
    ############ divide timestamps and token IDs in separate arrays. discards end boundaries (words currently might not have end boundaries)
    detected_start_times = []
    deteceted_tokens = []
    
    for section in detectedTokenList:
        parse_tokens_section(detected_start_times, deteceted_tokens, section)
   
    if with_section_annotations == 0:
       test_file_basis = 'persistent/umbrella_line.' 
    elif with_section_annotations == 1:
        test_file_basis = 'persistent/talkin_in_my_sleep.sections.'
    elif with_section_annotations == 2:
        test_file_basis = 'persistent/talkin_in_my_sleep.timed_lines.'
    if ParametersAlgo.POLYPHONIC:
        test_file_name = test_file_basis + detection_token_level + '.poly.lab.txt'
    else:
        test_file_name = test_file_basis + detection_token_level + '.lab.txt'
    reference_detected_token_list_URI = os.path.join(testDir, test_file_name)
    if detection_token_level == 'phonemes':
        reference_tokens, reference_start_times, _ = load_delimited(reference_detected_token_list_URI, [str, float, float], delimiter='\t')
    elif detection_token_level == 'words' or detection_token_level == 'lines':
        reference_tokens, reference_start_times = load_delimited(reference_detected_token_list_URI, [str, float], delimiter='\t')
    else:
        sys.exit('unsupported detection level ' + str(detection_token_level) )    
    return reference_start_times, detected_start_times, reference_tokens, deteceted_tokens


def parse_tokens_section(detected_start_times, deteceted_tokens, token_list):
    '''
    divide into a list of tokens and list of timestamps. Add '.' for end-of-line tokens to match format of the stored reference file. 
    '''
    for token in token_list:
        detected_start_times.append(token.start_ts)
        if token.text == '' and ParametersAlgo.STORE_DOTS: # DANGER: this does not make sence for level phonemes
            token.text = '.'
        deteceted_tokens.append(token.text) # load persistently stored

def test_path_to_tokenlist():
    '''
    test the conversion of detected path to a detected token list. in other words tests method   expand_path_to_<s.th>_List
    Tests two token levels: words and phonemes
    
    '''
    ### load stored path
    path_pers_URI = os.path.join(testDir,'persistent/path_umbrella_line.json')
    with open(path_pers_URI, 'r') as f:
       path_raw = json.load(f)
    path = Path() 
    path.setPathRaw(path_raw)
    
    ParametersAlgo.END_TS = 1
    
    for ParametersAlgo.DETECTION_TOKEN_LEVEL in ['lines','phonemes', 'words']:
    
        with_section_annotations = 0 # no persistent tokens  prepared for phonemes in  with_section_annotations={1,2}
        
        ### prepare lyrics of recording. do not change input, run_backtrack hard coded to work with umbrella_line
        recording = setUp_recording(with_section_annotations, with_shortest_audio=True)
        recording.sectionLinks[0].createLyricsModels() # 1 section only becasue  with_section_annotations = 0
        lyrics_models = recording.sectionLinks[0].lyricsWithModels
        
        if ParametersAlgo.DETECTION_TOKEN_LEVEL == 'lines':
            #  line timestamps from each first word in line
            detectedTokenList = expand_path_to_wordList (lyrics_models, path, _constructTimeStampsForTokenDetected)            
            detected_lines_list = word_list_to_line_list(lyrics_models.lyrics, detectedTokenList, ParametersAlgo.END_TS)
            assert "because when the sun shines" == detected_lines_list[0].text
            assert 1.53 == detected_lines_list[0].start_ts
            assert 2.52 == detected_lines_list[0].end_ts
            
            assert "we shine together" == detected_lines_list[1].text
            assert 2.62 == detected_lines_list[1].start_ts
            assert 4.02 == detected_lines_list[1].end_ts
        else:
            if ParametersAlgo.DETECTION_TOKEN_LEVEL == 'words': 
                detectedTokenList = expand_path_to_wordList (lyrics_models, path, _constructTimeStampsForTokenDetected)            
            elif ParametersAlgo.DETECTION_TOKEN_LEVEL ==  'phonemes':
                detectedTokenList = expand_path_to_phonemes_list(lyrics_models.statesNetwork, path, _constructTimeStampsForTokenDetected)
             
            pers_start_times, detected_start_times, pers_tokens, deteceted_tokens = prepare_detected_and_reference_data([detectedTokenList], ParametersAlgo.DETECTION_TOKEN_LEVEL, with_section_annotations)
             
            assertListsEqual(pers_start_times, detected_start_times) # times of tokens
            assertListsEqual(pers_tokens, deteceted_tokens) # ids of tokens
        


def test_decoded_phoneme_sequence_meaningful():
    '''
    if the decoded  sequence of  phonemes makes sense. 
    Sometimes it does not finish with expected silence at the end of phrase  
    '''
    recording = setUp_recording(with_section_annotations=0)
    
    # breaks for these cases due to not correct timed_lyrics. 
#     audioFileURI =  '/Users/joro/Documents/VOICE_magix/smule/dataset/101935856_2505827/1528828642_1904126862.wav'
#     lyrics_URI =  '/Users/joro/Documents/VOICE_magix/smule/dataset/101935856_2505827//timed_lyrics.txt'
#     vocal_intervals_URI = '/Users/joro/Documents/VOICE_magix/smule/dataset/segs/101935856_2505827/1528828642_1904126862_segs.txt' 
    
    vocal_intervals_URI = os.path.join(projDir, 'test/example/umbrella_line_vocal_segs.txt')
    EXPECTED_ORDER = 1
    recording.vocal_intervals_to_section_links(vocal_intervals_URI = vocal_intervals_URI) 

    la = LyricsAligner(recording, EXPECTED_ORDER, ParametersAlgo.PATH_TO_HCOPY)
    _, decoders, _ = la.alignRecording()
    
    for decoder in decoders:
        lyrics = decoder.sectionLink.section.lyrics
        if is_detected_path_meaningful(lyrics, decoder.path): assert 1
        else: assert 0 
     

if __name__ == '__main__':
#     test_BackTrack()
    test_path_to_tokenlist()
#     test_decoded_phoneme_sequence_meaningful()
#     test_get_segment_path()
#     test_calc_phi_indices()