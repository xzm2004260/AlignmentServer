# Lyrics-to-audio alignment with syllable duration modeling
""" please cite:
Dzhambazov, G., & Serra X. (2015).  Modeling of Phoneme Durations for Alignment between Polyphonic Audio and Lyrics.
Sound and Music Computing Conference 2015.
"""


import logging
import os
import sys
import time
import numpy as np


### include src folder
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if parentDir not in sys.path:
    sys.path.append(parentDir)

from src.hmm.continuous.MLPHMM import load_MLPs_and_config
from src.align._SyllableBase import SIL_TEXT
from src.align.FeatureExtractor import FeatureExtractor, MODEL_PATH, load_audio_mono
from src.align.ParametersAlgo import ParametersAlgo
if ParametersAlgo.POLYPHONIC:
    from src.align.separate import separate
 
# from src.onsets.OnsetDetector import OnsetDetector

from .Decoder import Decoder
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir, os.path.pardir,)) 

VOCAL_LABELS = ['.vocal', '.non-vocal']
# from evalPhonemes import eval_percentage_correct_phonemes, display



projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir )) 

modelDIR = projDir + '/models_makam/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'



from src.utilsLyrics.Utilz import  addTimeShift,  determineSuffix



ANNOTATION_EXT = '.TextGrid'
 
logger = logging.getLogger(__name__)
loggingLevel = ParametersAlgo.LOGGING_LEVEL
# loggingLevel = logging.DEBUG
# loggingLevel = logging.INFO

logging.basicConfig(format='%(levelname)s:%(funcName)30s():%(message)s')
logger.setLevel(loggingLevel)


class LyricsAligner():
    def __init__(self, recording,  EXPECTED_ORDER, path_to_hcopy):
        
        self.recording = recording
        self.EXPECTED_STRUCTURE = EXPECTED_ORDER # the order of lyrics is the same as it is sung
        self.path_to_hcopy = path_to_hcopy
        self.tokenLevelAlignedSuffix = determineSuffix(ParametersAlgo.WITH_DURATIONS, ParametersAlgo.WITH_ORACLE_PHONEMES,\
                                                        ParametersAlgo.WITH_ORACLE_ONSETS, ParametersAlgo.DETECTION_TOKEN_LEVEL, ParametersAlgo.OBS_MODEL, ParametersAlgo.Q_WEIGHT_TRANSITION)
        
        from datetime import datetime
        dateTimeEnd = "2017-12-27 23:00:00"
        self.dateEnd = datetime.strptime(dateTimeEnd, "%Y-%m-%d %H:%M:%S")



        self.acoustic_model = None
        if ParametersAlgo.FOR_MAKAM:
            if ParametersAlgo.OBS_MODEL == 'GMM': # load htk parser
                pathHTKParser = os.path.join(parentDir, 'htkModelParser')
                if pathHTKParser not in sys.path:    
                    sys.path.append(pathHTKParser)
                from htkparser.htk_converter import HtkConverter
                self.acoustic_model = HtkConverter()
                self.acoustic_model.load(MODEL_URI, HMM_LIST_URI)
        
        elif ParametersAlgo.FOR_JINGJU:
            #### read models done in LyricsWithModels depending 
#             self.model = self.recording.which_fold
            self.acoustic_model = 'fold1'
        
        else: # for english, 
            if ParametersAlgo.OBS_MODEL == 'MLP':
                time0 = time.time()
                self.acoustic_model, self.cfg_acoustic_model = load_MLPs_and_config() # load network
                time1 = time.time()
                logger.debug(" loading DNN model: {} seconds".format(time1-time0) )
            else:
                sys.exit('not implemented')


    def alignRecording(self ):
            '''
            align each section link
            
            output_URI: str
                output_URI for one section. So far only storing of results for each section separately supported. 
                Since we support one section, output_URI is for one section. 
            
            Return
            ----------------------- 
            detected token list
            '''
            
            decoders = [] # TODO: make decoder a field of current section link and feature extractor field of decoder
                        
            complete_recording_detected_token_list = []    
            complete_recording_phi_segments  = []
            
            for  currSectionLink in self.recording.sectionLinks :
                    if self.recording.duration < currSectionLink.endTs:
                        sys.exit('section link ends over the end of the recording' )
                    
                    if not hasattr(currSectionLink, 'section') or currSectionLink.section == None:
                        print(("skipping sectionAnno {} not matched to any score section ...".format(currSectionLink)))
                        continue   
                    lyrics = currSectionLink.section.lyrics
         
                    if len(lyrics.listWords) == 0:    
                        print(("skipping sectionLink {} with no lyrics ...".format(currSectionLink.melodicStructure)))
                        continue 
                    decoder = self.prepare_decoder(    currSectionLink)
                    currSectionLink.detectedTokenList,  lines_max_phi_segments = self.align_lyrics_section(decoder, currSectionLink)
                    
                    if not is_detected_path_meaningful(lyrics, decoder.path) and len(currSectionLink.non_vocal_intervals) != 0: 
                        logger.warning('Realigning recording segment from time {} to time {} without non-vocal segments'.format(currSectionLink.beginTs, currSectionLink.endTs) )
                        currSectionLink.non_vocal_intervals = np.array([]); decoder = self.prepare_decoder(currSectionLink)
                        currSectionLink.detectedTokenList,  lines_max_phi_segments = self.align_lyrics_section(decoder, currSectionLink)
                        if not is_detected_path_meaningful(lyrics, decoder.path):
                            sys.exit('Recording segment from time {} to time {} cannot be aligned.'.format(currSectionLink.beginTs, currSectionLink.endTs))    
                    
                    decoders.append(decoder)
                    if len(complete_recording_detected_token_list) > 0 and self.recording.with_section_anno != 0: # do not check at first section/line
                        complete_recording_detected_token_list = fix_non_meaningful_timestamps(complete_recording_detected_token_list, currSectionLink.detectedTokenList) # this is introduced for lines, it should not be needed for sections
                    complete_recording_detected_token_list.extend(currSectionLink.detectedTokenList)
                    complete_recording_phi_segments.extend(lines_max_phi_segments)

            
                        
            return complete_recording_detected_token_list, decoders, complete_recording_phi_segments # decoders is returned for access to decoding fields for control               
               


    def  prepare_decoder( self,    currSectionLink):
            '''
            load decoder object for current section link
            '''
                
            from datetime import date
            a = False
                
            fe = FeatureExtractor(self.path_to_hcopy, currSectionLink) 
            
            if self.dateEnd.date() < date.today():
                a = True
            
            onsetDetector  = None
            
#             if a:
#                 sys.exit('The licensed trial version has expired. Please contact info@voicemagix.com')
            
            # normalization needed for source sep
            audio, sampleRate = load_audio_mono(self.recording.recordingNoExtURI + '.wav', with_normalization_max=ParametersAlgo.POLYPHONIC) 
 
             
            # segregate vocal part from whole recording
            if ParametersAlgo.POLYPHONIC: 
                model_URI = os.path.join(MODEL_PATH,   'krast.dad')
                logger.info("doing source separation for recording: {} ...".format(self.recording.recordingNoExtURI) )
                 
 
                if sampleRate != 44100:    # source separation is hard coded to work with 44100.
                        sys.exit('sample rate is not 44100. source separation is hard coded to work with 44100')
                time0 = time.time()
                audio = separate( audio, model_URI,0.3,30,25,32,513)
                time1 = time.time()
                logger.info(" source separation: {} seconds".format(time1-time0) )
 
            
            else:
                logger.info(" A cappella desired. Skipping source separation for recording: {} ...".format(self.recording.recordingNoExtURI) )
 
            #  extract audio features for a section link
                             
            time0 = time.time()
            fe.featureVectors = fe.loadMFCCs(audio, currSectionLink,  sampleRate) #     featureVectors = featureVectors[0:1000]
            time1 = time.time()
            logger.debug(" mfcc extraction: {} seconds".format(time1-time0) )
 
            currSectionLink.createLyricsModels( fe.featureVectors)
             
#                 if logger.level == logging.DEBUG:
#                     currSectionLink.lyricsWithModels.printWordsAndStates()
#                         currSectionLink.lyricsWithModels.lyrics.printPhonemeNetwork()
        #################### decode
            time0 = time.time()
            decoder = Decoder(currSectionLink, self.acoustic_model, self.cfg_acoustic_model)
            time1 = time.time()
            logger.debug(" hmm network creation (incl. trans matrix): {} seconds".format(time1-time0) )
            
            decoder.caclulate_Bmap(fe, onsetDetector) 
            
            return decoder
      
        
    def align_lyrics_section(self, decoder, currSectionLink):
        '''
        actual forced alignment and its output
        TODO: document better what it returns 
        '''
        detectedTokenList = decoder.decodeAudio()             # decode most probable alignment path
        detectedTokenList = addTimeShift(detectedTokenList,  currSectionLink.beginTs)
        
        phi = decoder.hmmNetwork.phi
        phi_segments = decoder.path.calc_phi_segments_lines(phi, currSectionLink.lyricsWithModels) # phi score for path segments corresponding to lyrics lines
        lyrics_lines = currSectionLink.lyricsWithModels.lyrics.lyrics_lines
        if len(lyrics_lines) != len(phi_segments):
            sys.exit('phi segments are {} while lyrics lines from text file are {} '\
                 .format(len(phi_segments), len(lyrics_lines) ) )
        lines_phis = list(zip(lyrics_lines, phi_segments))
        
        return detectedTokenList, lines_phis

    
def getSectionLinkBybeginTs(sectionLinks, queryBeginTs):
    for sectionLink in sectionLinks:
        if str(sectionLink.beginTs) ==  queryBeginTs:
            return sectionLink


def fix_non_meaningful_timestamps(existing_token_list, incoming_token_list):
    '''
    replace potentially non-monotonously increasing timestamps at the end of a section
    due to GenericRecording.TOLERANCE_END_SECTION window
    stategy: keep incoming list first token's timestamp and replace the timstamps of last tokens from existing list, 
    by squeezing them equally in a meaningful time interval  
    '''
    
    last_token_so_far = existing_token_list[-1]
    incoming_token = incoming_token_list[0]
    
    if ParametersAlgo.DETECTION_TOKEN_LEVEL == 'phonemes':
        sys.exit('section annotations not implemented with phonemes')
    if last_token_so_far[-1] == '' and incoming_token[-1] == '': # remove two repeated '.'-s
        del incoming_token_list[0]
    
    incoming_token = incoming_token_list[0] # first incoming non-'.' token
    correct_ts = incoming_token[0] # assume this time is correct 
    idx = -1
    while existing_token_list[idx][0] > correct_ts: # reverse  a couple of previous that are not ok in ref to the ''correct'' one
        idx-=1
    closest_correct_ts = existing_token_list[idx][0]
    
    num_incorrect_tokens = -1 - idx
    if num_incorrect_tokens != 0: # correct increasing back until the end
        idx = idx + 1
        time_to_allocate = float(correct_ts - closest_correct_ts) 
        time_share =  time_to_allocate / float(num_incorrect_tokens + 1)
        for i in range(num_incorrect_tokens):
            existing_token_list[idx + i][0] = closest_correct_ts + float(i + 1) * time_share
    
    return existing_token_list

 
def average_phi_segments(complete_recording_phi_segments):
     #             if with_section_anno != 0:
    phis = []
    for line_and_phi in complete_recording_phi_segments:
        phis.append(line_and_phi[1])
    averagePhiScore = sum(phis) / float(len(complete_recording_phi_segments))
#     print 'min phi:', min(phis)
#     print 'max phi:', max(phis)
    return averagePhiScore  


def pick_skipped_phonemes(lyrics, path):
    '''
    for the given lyrics pick the states in the decoded path which are not in decoded path (i.o.w. are skipped)
    '''
    len_states_in_transcript = len(lyrics.phonemesNetwork)  # assumes a phoneme has one state
    
    if not hasattr(path, 'indicesStateStarts'):
        sys.exit('method  path.path2stateIndices() has to be run first  ')
    
    if len( path.indicesStateStarts ) == len_states_in_transcript:
       return []
    
    decoded_state_idces = []
    for i in range(len(path.indicesStateStarts)):  # get the unique decoded states
       decoded_state_idx = path.pathRaw[path.indicesStateStarts[i]]
       decoded_state_idces.append(decoded_state_idx)
    
    all_states = set(range(len_states_in_transcript))
    return all_states.difference(set(decoded_state_idces)) 

def is_detected_path_meaningful(lyrics, path):
    '''
    Consider path non meaningful 
    if in path there is a skipped phoneme different than silent phoneme 
    '''
    phoneme_indices = pick_skipped_phonemes(lyrics, path)
    #         lyrics.printPhonemeNetwork()
    for idx in phoneme_indices:
            if lyrics.phonemesNetwork[idx].ID != SIL_TEXT: # there should not be any phoneme diferent than silent phoneme
                return False
    return True