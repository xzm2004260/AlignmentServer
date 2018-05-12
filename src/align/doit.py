'''
Created on Aug 31, 2017

@author: joro
'''
import os
import sys
import logging


projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

from src.for_english.CMUWord import CMUWord
from src.utilsLyrics.Utilz import write_decoded_to_file
from src.align.LyricsAligner import LyricsAligner, average_phi_segments
from src.align.ParametersAlgo import ParametersAlgo
from src.align.GenericRecording import GenericRecording
from src.align.Phonetizer import Phonetizer

EXPECTED_ORDER = 1 # the order of lyrics is sung the same way (expected) as  written



def create_recording(audioFileURI, lyrics_URI, with_section_annotations=0, is_test_case=False):
    '''
    helper method for a couple of lines that create recording object and its lyrics
    '''
    fn_dict = os.path.join(projDir, 'src/for_english/cmudict.0.6d.syll')
    Phonetizer.initPhoneticDict(ParametersAlgo.POLYPHONIC, fn_dict)
    
    recording = GenericRecording(audioFileURI)

    CMUWord.input_func_name = prompt_for_input
    if is_test_case:
        CMUWord.input_func_name = lambda _:'y' # do not stop on asking for input, otherwise test breaks

    recording.load_lyrics(lyrics_URI, with_section_annotations)
    return recording

def prompt_for_input():
        return input('lyrics contain a suspicious word. Are you sure this is part of the sung lyrics? [y/n] ')         


def align_CMU(audioFileURI, lyrics_URI,  output_URI, with_section_annotations=0, vocal_intervals_URI=None):
    '''
    top-level call method for English audio with CMU dictionary
    '''
    if os.path.isfile(output_URI) and \
    (ParametersAlgo.LOGGING_LEVEL == logging.DEBUG or ParametersAlgo.LOGGING_LEVEL == logging.INFO) : # at production does not stops
        logging.info('recording already aligned in file {}'.format(output_URI))
        return
        #                     detectedTokenList, phiOptPath, detectedPath = read_decoded(URIRecordingChunkResynthesizedNoExt, detectedAlignedfileName)
    logging.info("working on recording {}".format(audioFileURI))

    recording = create_recording(audioFileURI, lyrics_URI, with_section_annotations)
#     print recording.sectionLinks[0].section.lyrics
#     return
    recording.vocal_intervals_to_section_links(vocal_intervals_URI = vocal_intervals_URI) 
#     recording.sectionLinks[0].section.lyrics.printPhonemeNetwork()
#     recording.sectionLinks[0].section.lyrics.printWords()
    la = LyricsAligner(recording, EXPECTED_ORDER, ParametersAlgo.PATH_TO_HCOPY) 
    detectedTokenList, _, recording_phi_segments  = la.alignRecording() # align
    
#          detectedAlignedfileName = currSectionLink.URIRecordingChunk + tokenLevelAlignedSuffix
    max_phi_score = average_phi_segments(recording_phi_segments)
    ###### write all decoded output persistently to files
    if ParametersAlgo.WRITE_TO_FILE:
            write_decoded_to_file(detectedTokenList, output_URI, max_phi_score, recording_phi_segments)                
     
    
    #init results
    sectionswise_detected_token_list = []
    
    for sectionLink in la.recording.sectionLinks:
        if not hasattr(sectionLink, 'detectedTokenList'):
            logging.warning('{} has no lyrics decoded'.format(sectionLink))
            continue
        sectionswise_detected_token_list.append(sectionLink.detectedTokenList)
      
    
    #     la.evalAccuracy(ParametersAlgo.EVAL_LEVEL)
        
    return sectionswise_detected_token_list


    
def doit_CMU(argv):
    
    if len(argv) != 6 and len(argv) != 5:
        sys.exit('usage: {} <audio_URI> <lyrics_URI> <with_section_anno> (optional: <vocal_intervals>) <output.lab>'.format(argv[0]))
    

        # setting both to 0 means default (English)
    ParametersAlgo.FOR_MAKAM = 0
    ParametersAlgo.FOR_JINGJU = 0
    
    # test with section links. polyphonic

#     # test of audio working 
    ParametersAlgo.POLYPHONIC = 0
    ParametersAlgo.WITH_ORACLE_ONSETS = -1
    ParametersAlgo.WITH_ORACLE_PHONEMES = 0
    # set WITH_DURATIONS in ParametersAlgo. it cannot be set here
    
#####################################################  test with section anno and acapella
    # On kora.s.upf.edu
#     ParametersAlgo.PATH_TO_HCOPY = '/homedtic/georgid/htkBuilt/bin/HCopy'
   
    audioFileURI = argv[1]
    lyrics_URI = argv[2]
    with_section_anno = int(argv[3])
    if len(argv) == 6:
        vocal_intervals_URI = argv[4]
        output_URI = argv[5]
    else:
        vocal_intervals_URI = None
        output_URI = argv[4]
        
    ret = align_CMU(audioFileURI, lyrics_URI, output_URI, with_section_anno, vocal_intervals_URI )

if __name__ == '__main__':
    doit_CMU(sys.argv)
       