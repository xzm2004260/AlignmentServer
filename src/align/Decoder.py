'''
Created on Oct 27, 2014

@author: joro
'''
import logging
import os
import sys
import subprocess
import time
import numpy

### include src folder
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

from src.align._SyllableBase import SIL_TEXT
from src.align.LyricsParsing import expand_lyrics_to_phonemes_list
from .LyricsParsing import expandlyrics2WordList, _constructTimeStampsForTokenDetected,\
    expandlyrics2SyllableList
from .ParametersAlgo import ParametersAlgo
if ParametersAlgo.VISUALIZE:
    from visualize import visualizeMatrix, visualizeBMap, visualizePath,\
    visualizeTransMatrix

sys.path.append(os.path.join(os.path.dirname(__file__), '../test'))


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 


if not ParametersAlgo.WITH_DURATIONS:
    pathHTKParser = os.path.join(parentDir, 'HMM')
    if pathHTKParser not in sys.path:    
        sys.path.append(pathHTKParser)



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 


logger = logging.getLogger(__name__)
loggingLevel = ParametersAlgo.LOGGING_LEVEL
# loggingLevel = logging.DEBUG
# loggingLevel = logging.INFO

logging.basicConfig(format='%(levelname)s:%(funcName)30s():%(message)s')
logger.setLevel(loggingLevel)

# other logger set in _ContinuousHMM



# in backtracking allow to start this much from end back`
BACKTRACK_MARGIN_PERCENT= 0.2
# BACKTRACK_MARGIN_PERCENT= 0.0


class Decoder(object):
    '''
    decodes one audio segment/chunk. 
    holds structures used in decoding and decoding result
    '''


    def __init__(self, sectionLink, acoustic_model, cfg_acoustic_model, numStates=None):
        '''
        Constructor
        '''
        self.sectionLink = sectionLink
        

        
        self.hmmNetwork = []
        if ParametersAlgo.WITH_ORACLE_ONSETS != -1:
            from src.onsets.OnsetSmoothing import OnsetSmoothingFunction
            self.onsetSmoothingFunction = OnsetSmoothingFunction(ParametersAlgo.ONSET_SIGMA_IN_FRAMES)
        
        self._constructHmmNetwork(acoustic_model, cfg_acoustic_model, numStates)
        self.hmmNetwork.logger.setLevel(ParametersAlgo.LOGGING_LEVEL)
        
        # Path class object
        self.path = None
    
    

#     def serializePosteriograms(self):
#         import pickle
#         URI_tmp = self.sectionLink.URIRecordingChunk + '.' + ParametersAlgo.OBS_MODEL + '.PPG.pkl'
#         if ParametersAlgo.OBS_MODEL == 'MLP' or ParametersAlgo.OBS_MODEL == 'MLP_fuzzy':
#             with open(URI_tmp, 'w') as f:
#                 pickle.dump(self.hmmNetwork.mlp_posteriograms.T, f)
#             
#         elif ParametersAlgo.OBS_MODEL == 'GMM':
#             with open(URI_tmp, 'w') as f:
#                 pickle.dump(self.hmmNetwork.B_map, f)
    
    def caclulate_Bmap(self, featureExtractor, onsetDetector=None, fromTsTextGrid=0, toTsTextGrid=0):
        '''
        initialize bmap using feature vectors
        init onsets if they are specified (!=None) 

        '''
        if not ParametersAlgo.WITH_ORACLE_PHONEMES:
            obs_model_type = ParametersAlgo.OBS_MODEL 
            if ParametersAlgo.OBS_MODEL == 'MLP_fuzzy':
                obs_model_type = 'MLP'
            
            self.hmmNetwork.set_PPG_filename(self.sectionLink.URIRecordingChunk + '.' + obs_model_type + '.PPG.pkl' )
            self.hmmNetwork.setNonVocal(self.sectionLink.non_vocal_intervals)
            
#         if ParametersAlgo.WITH_ORACLE_PHONEMES == -1:
#             lenFeatures = 80
#             self._mapBStub(lenFeatures)
#         elif ParametersAlgo.WITH_ORACLE_PHONEMES == 1: # with phoneme annotations as feature vectors
#                 
#                 durInSeconds = toTsTextGrid - fromTsTextGrid
#                 lenFeatures = tsToFrameNumber(durInSeconds - ParametersAlgo.WINDOW_LENGTH / 2.0) 
#                 self._mapBOracle( featureExtractor.featureVectors, lenFeatures, fromTsTextGrid)
#         else: # with featureVectors
        self.hmmNetwork._mapB(featureExtractor.featureVectors)

        
        lenFeatures = len(featureExtractor.featureVectors)
        if onsetDetector is not None: # DO NOT REIMPLEMENT in C++ onset-related logic
            self.noteOnsets = onsetDetector.onsetTsToOnsetFrames( lenFeatures)
     
            

    def decodeAudio( self):
        ''' decode path for given exatrcted features for audio
        HERE is decided which decoding scheme: with or without duration (based on WITH_DURATION parameter)
        '''
        if ParametersAlgo.DECODE_WITH_HTK:
            detectedWordList = self.decodeAudioWithHTK()
            return detectedWordList
        
        
        # standard viterbi forced alignment
        if not ParametersAlgo.WITH_DURATIONS:
            time0 = time.time()
            self.hmmNetwork.B_map = numpy.log(self.hmmNetwork.B_map) # convert to log domain
            self.hmmNetwork.transMatrix = numpy.log(self.hmmNetwork.transMatrix) # convert to log domain
           #         np.savetxt('B_map_umbrella_line.txt', self.hmmNetwork.B_map)
#             np.savetxt('trans_matrix_umbrella_line.txt', self.hmmNetwork.transMatrix)

#             psiBackPointer = self.hmmNetwork.viterbi_fast_forced_python()
            psiBackPointer = self.hmmNetwork.viterbi_fast_forced()
            time1 = time.time()
            logger.debug(" Viterbi: {} seconds".format(time1-time0) )

            chiBackPointer = None
#            for kimseye region with note onsets for ISMIR poster SHi-KA-YET:
            if ParametersAlgo.VISUALIZE:
                self.hmmNetwork.visualize_trans_probs(self.sectionLink.lyricsWithModels, 685,1095, 13,19)
        
        else:   # duration-HMM
            chiBackPointer, psiBackPointer = self.hmmNetwork._viterbiForcedDur()
            
        time0 = time.time()
        detectedWordList, self.path = self.backtrack(chiBackPointer, psiBackPointer )
        time1 = time.time()
        logger.debug(" backtracking: {} seconds".format(time1-time0) )


        if ParametersAlgo.VISUALIZE:
            ax = visualizeBMap(self.hmmNetwork.B_map)        
#             visualizePath(ax,self.path.pathRaw, self.hmmNetwork.B_map)

#             ax = visualizeMatrix(self.hmmNetwork.phi, 'phi' )
#             ax = visualizeMatrix(self.hmmNetwork.psi, 'psi' )
            visualizePath(ax,self.path.pathRaw, self.hmmNetwork.B_map)

            
#         self.path.printDurations() #DEBUG
        
        return detectedWordList
    

    
        
    def _constructHmmNetwork(self, acoustic_model, cfg_acoustic_model, numStates ):
        '''
        top level-function: construct super-hmm by concatenating all phonemes from lyrics transcription 
        
        Returns:
        self.hmmNetwork: of type GMHMM, MLPHMM or MLP_fuzzyMappedHMM

        '''

        ######## construct transition matrices with note onsets
#         transMatrices = None
#         if not ParametersAlgo.WITH_DURATIONS:
#             # construct means, covars, and all the rest params
#             #########    
#             transMatrices = list()
#             if ParametersAlgo.WITH_ORACLE_ONSETS ==0 or ParametersAlgo.WITH_ORACLE_ONSETS ==1: # using onsets
#                 for onsetDist in range(ParametersAlgo.ONSET_SIGMA_IN_FRAMES + 1):
#                     transMatrices.append( _constructTransMatrix(self.sectionLink.lyricsWithModels, onsetDist) )
#             # not using onsets, only one matrix 
#             transMatrices.append( _constructTransMatrix(self.sectionLink.lyricsWithModels,  onsetDist = ParametersAlgo.ONSET_SIGMA_IN_FRAMES + 1) ) # last one with max distance
        

        
        if ParametersAlgo.OBS_MODEL == 'MLP':
            from src.hmm.continuous.MLPHMM  import MLPHMM
            self.hmmNetwork = MLPHMM(self.sectionLink.lyricsWithModels.statesNetwork, acoustic_model, cfg_acoustic_model)
        elif ParametersAlgo.OBS_MODEL == 'MLP_fuzzy':
            from src.hmm.continuous.MLP_fuzzyMappedHMM  import MLP_fuzzyMappedHMM
            self.hmmNetwork = MLP_fuzzyMappedHMM(self.sectionLink.lyricsWithModels.statesNetwork)
        elif ParametersAlgo.OBS_MODEL == 'CNN':
            from src.hmm.continuous.CNNHMM  import CNNHMM
            self.hmmNetwork = CNNHMM(self.sectionLink.lyricsWithModels.statesNetwork)
        elif ParametersAlgo.OBS_MODEL == 'GMM': 
            sys.exit('GMMs models not implemented')

        

        



    def path2ResultTokenList(self, path, tokenLevel='words'):
        '''
        makes sense of path indices : maps numbers to states and phonemes.
        uses self.sectionLink.lyricsWithModels.statesNetwork and self.sectionLink.lyricsWithModels.listWords) 
        to be called after decoding
        
        Parameters:
        path of type hmm.Path
        '''
        # indices in pathRaw
        self.path = path
#         self.path.path2stateIndices() # TODO: remove, because called second time
        if not hasattr(path, 'indicesStateStarts'):
            sys.exit('sequence of phonemes not decoded with Path object') 
        
        #sanity check
        numStates = len(self.sectionLink.lyricsWithModels.statesNetwork)
        numdecodedStates = len(self.path.indicesStateStarts)
        
        if ParametersAlgo.WITH_DURATIONS:
            if numStates != numdecodedStates:
                logging.warn("detected path has {} states, but stateNetwork transcript has {} states \n \
                WORKAROUND: adding missing states at beginning of path. This should not happen often ".format( numdecodedStates, numStates ) )
                # num misssed states in the beginning of the path
                howManyMissedStates = numStates - numdecodedStates
                # WORKAROUND: assume missed states start at time 0. Append zeros
                for i in range(howManyMissedStates):
                    self.path.indicesStateStarts[:0] = [0]
        
        if tokenLevel == 'words':
            if ParametersAlgo.FOR_JINGJU:
                sys.exit('token leven cannot be words, there are no words in Mandarin')
            detectedTokenList = expandlyrics2WordList (self.sectionLink.lyricsWithModels, self.path, _constructTimeStampsForTokenDetected)
        elif tokenLevel == 'syllables':
            detectedTokenList = expandlyrics2SyllableList (self.sectionLink.lyricsWithModels, self.path, _constructTimeStampsForTokenDetected)
        elif tokenLevel == 'phonemes':
            detectedTokenList = expand_lyrics_to_phonemes_list(self.sectionLink.lyricsWithModels.statesNetwork, self.path, _constructTimeStampsForTokenDetected)
        else:   
            detectedTokenList = []
            logger.warning( 'parsing of detected  {} not implemented'.format( tokenLevel) )
            
        return detectedTokenList 
    
    
    
    def backtrack(self, chiBackPointer, psiBackPointer):
        ''' 
        backtrack optimal path of states from backpointers
        interprete the state sequence to words      
        '''
        
        # self.hmmNetwork.phi is set in decoder.decodeAudio()
        from src.hmm.Path import Path
        self.path =  Path( psiBackPointer, chiBackPointer ) # actual backtracking
        

               

        if ParametersAlgo.WITH_ORACLE_PHONEMES:
            outputURI = self.sectionLink.URIRecordingChunk + '.path_oracle'
        else:
            outputURI = self.sectionLink.URIRecordingChunk + '.path'
        
#         writeListToTextFile(self.path.pathRaw, None , outputURI)
        
        detectedTokenList = self.path2ResultTokenList(self.path, ParametersAlgo.DETECTION_TOKEN_LEVEL)
        
        # DEBUG info
#         if logger.level == logging.DEBUG:
#             path.printDurations() # not working
        return detectedTokenList, self.path


    def defineForwardTransProbs_onsets(self, statesNetwork, idxCurrState, onsetDist):
        '''
        at onset present, change trasna probs based on rules.
        consider special case sp
        Inciorporated onsets-releated logic in a way that is hard to remove
        '''
        
        nextStateWithDur = statesNetwork[idxCurrState+1]
        currStateWithDur = statesNetwork[idxCurrState]
                    
     
        if not ParametersAlgo.ONLY_MIDDLE_STATE:
            sys.exit("align.Decoder.defineWaitProb  implemented only for 1-state phonemes ")
        
    #     if idxState == len(statesNetwork)-1: # ignore onset at last phonemes
    #         return currStateWithDur.getWaitProb()
        
        currPhoneme = currStateWithDur.phoneme
        nextPhoneme = nextStateWithDur.phoneme
        
        # normally should go to only next state as in forced alignment
        forwProb1 = self.calcForwProbWithRules(currStateWithDur, nextStateWithDur, onsetDist )
        forwProb2 = 0
        
        if nextPhoneme.ID == SIL_TEXT and (idxCurrState+2) < len(statesNetwork):   #### add skipping forward trans prob
            
            ### skipping sp to next state
            nextNextStateWithDur = statesNetwork[idxCurrState+2]
            currPhoneme.setIsLastInSyll(1) # 
            forwProb2 = self.calcForwProbWithRules(currStateWithDur, nextNextStateWithDur, onsetDist )
            currPhoneme.setIsLastInSyll(0)
            
    
    
        return forwProb1, forwProb2
        
 
        


    def calcForwProbWithRules(self, currStateWithDur, followingStateWithDur, onsetDist):
        '''
        Rules for transition from one to next phoneme
        '''  
        currPhoneme = currStateWithDur.phoneme
        followingPhoneme = followingStateWithDur.phoneme
        forwProb = 1 - currStateWithDur.getWaitProb()
        onsetWeight = self.onsetSmoothingFunction.calcOnsetWeight(onsetDist)
        
        if currPhoneme.isLastInSyll(): # inter-syllable
                if currPhoneme.isVowel() and not followingPhoneme.isVowelOrLiquid(): # rule 1
                    return max(forwProb - onsetWeight * ParametersAlgo.Q_WEIGHT_TRANSITION, 0.01) # 0.1 instead of 0 becasue log(0) will give -inf
                elif not currPhoneme.isVowelOrLiquid() and followingPhoneme.isVowelOrLiquid(): # rule 2
                    return forwProb + onsetWeight * ParametersAlgo.Q_WEIGHT_TRANSITION 
        else: # not last in syllable, intra-syllable
                if currPhoneme.isVowel() and not followingPhoneme.isVowel(): # rule 3
                    return max(forwProb - onsetWeight * ParametersAlgo.Q_WEIGHT_TRANSITION, 0.01)
                elif not currPhoneme.isVowelOrLiquid() and followingPhoneme.isVowelOrLiquid(): # rule 4
                    return forwProb + onsetWeight * ParametersAlgo.Q_WEIGHT_TRANSITION
                elif currPhoneme.isVowel() and followingPhoneme.isVowel():
                    logging.warning("two consecutive vowels {} and {} in a syllable. not implemented! Make sure ONLY_MIDDLE_STATE is set true. 3-state models not implemented".format(currPhoneme.ID, followingPhoneme.ID))
                    return forwProb
        
        #  onset has no contribution in other cases    
        return forwProb



    
def alignWithHTK(URIRecordingChunkNoExt, dict_, mlf):
    #     
    #     pipe = subprocess.Popen([PATH_TO_HVITE, '-l', "'*'", '-A', '-D', '-T', '1', '-b', 'sil', '-C', PATH_TO_CONFIG_FILES + 'config_singing', '-a', \
    #                                  '-H', self.pathToHtkModel, '-H',  DUMMY_HMM_URI , '-H',  MODEL_NOISE_URI , '-i', '/tmp/phoneme-level.output', '-m', \
    #                                  '-w', wordNetwURI, '-y', 'lab', dictName, PATH_TO_HMMLIST, mfcFileName], stdout=self.currLogHandle)
        
        logName = '/tmp/log_all'
        currLogHandle = open(logName, 'w')
        currLogHandle.flush()
        decodedWordlevelMLF = URIRecordingChunkNoExt + '.out.mlf'    
            
        
        path, fileName = os.path.split(URIRecordingChunkNoExt)
        path, fold = os.path.split(path) # which Fold
        
        PATH_HTK_MODELS = '/home/georgid/Documents/JingjuSingingAnnotation-master/lyrics2audio/models/hmmdefs_' + fold 
        PATH_TO_HMMLIST = ' /home/georgid/Documents/JingjuSingingAnnotation-master/lyrics2audio/models/hmmlist'
           
        command = [ParametersAlgo.PATH_TO_HVITE, '-a', '-m', '-I', mlf, '-C', ParametersAlgo.PATH_TO_CONFIG_FILES + 'config',  \
                                     '-H', PATH_HTK_MODELS,  '-i', decodedWordlevelMLF,  \
                                      dict_, PATH_TO_HMMLIST, URIRecordingChunkNoExt + '.wav']   
        pipe = subprocess.Popen(command, stdout = currLogHandle)
            
        pipe.wait()      
        return decodedWordlevelMLF

