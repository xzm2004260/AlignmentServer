'''
Created on May 28, 2015

@author: joro
'''

### include src folder
import os
import sys
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if parentDir not in sys.path:
    sys.path.append(parentDir)
    
import logging

######### PARAMS:
class ParametersAlgo(object):
    
    SKIP_ALREADY_ALIGNED = 0
    LOGGING_LEVEL = logging.WARNING # used in production to skip info and debug messages
#     LOGGING_LEVEL = logging.INFO
    LOGGING_LEVEL = logging.DEBUG
    
    POLYPHONIC = 0

    FOR_JINGJU = 0
    FOR_MAKAM = 0
    
     # always set here only
    OBS_MODEL = 'GMM' 
    OBS_MODEL = 'MLP'
#     OBS_MODEL = 'CNN' 
    
                
    # use duraiton-based decoding (HMMDuraiton package) or just plain viterbi (HMM package) 
    # if false, use transition probabilities from htkModels
    WITH_DURATIONS= 0 # always set here only
         
    WITH_ORACLE_ONSETS = -1 ### no onsets at all
    
    USE_PERSISTENT_PPGs = 0
    
    # level into which to segments decoded result stateNetwork
#     DETECTION_TOKEN_LEVEL= 'syllables'
    DETECTION_TOKEN_LEVEL = 'words'
#     DETECTION_TOKEN_LEVEL = 'lines'
#     DETECTION_TOKEN_LEVEL= 'phonemes'
    
    # unit: num frames, equiv to 1/hoplength
    NUMFRAMESPERSECOND = 100
    # same as WINDOWSIZE in htk's wavconfig singing. unit:  seconds. TOOD: read from there automatically
    WINDOW_LENGTH = 0.025
    
    # in frames
    
    ONLY_MIDDLE_STATE = 1
    
    WITH_SHORT_PAUSES = 0 # short pause after each word
    
    # padded a short pause state at beginning and end of complete lyric sequence
    WITH_PADDED_SILENCE = 1
    
    # no feature vectors at all. all observ, probs. set to 1
#     WITH_ORACLE_PHONEMES = -1
    WITH_ORACLE_PHONEMES = 0
    
    
    # in _ContinousHMM.b_map cut probabilities
    CUTOFF_BIN_OBS_PROBS = 30
    
    THRESHOLD_PEAKS = -65

    

    
    VISUALIZE = 0
    
    ANNOTATION_RULES_ONSETS_EXT = 'annotationOnsets.txt'
    ANNOTATION_SCORE_ONSETS_EXT = 'alignedNotes.txt' # use this ont to get better impression on recall, compared to annotationOnsets.txt, which are only on note onsets with rules of interest 
    
    WRITE_TO_FILE = 0
    
    
    
    Q_WEIGHT_TRANSITION = 3.5 # onset-related. TODO: clean up

    ########## DURATION-related
    CONSONANT_DURATION_IN_SEC = 0.1 
    CONSONANT_DURATION = NUMFRAMESPERSECOND * CONSONANT_DURATION_IN_SEC;
    GLOBAL_WAIT_PROB = 0.9
    ALPHA = 0.97
    DEVIATION_IN_SEC = 0.1
    CONSONANT_DURATION_DEVIATION = 0.7
    
    ####### htk-related
    MFCC_HTK = 1  # extract mfccs with htk. if =0 uses essentia (not exactly reproducing htk's mfcc type)

    DECODE_WITH_HTK = 0

    PATH_TO_HCOPY= '/usr/local/bin/HCopy'
    PATH_TO_HVITE = '/usr/local/bin/HVite'

    projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.path.pardir ))
    PATH_TO_CONFIG_FILES= projDir + '/models_makam/input_files/'    
    