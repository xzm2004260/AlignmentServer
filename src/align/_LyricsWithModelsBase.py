'''
Created on Oct 27, 2014

@author: joro
'''

### include src folder
import os
import sys
import copy
import queue
import math
import logging

from src.align._PhonemeBase import PhonemeBase
from src.align._SyllableBase import SIL_TEXT
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)
    
from .Constants import NUM_FRAMES_PERSECOND
from .ParametersAlgo import ParametersAlgo

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir, os.path.pardir)) 
    
from src.hmm.StateWithDur import StateWithDur

from .Decoder import logger

from src.hmm.Parameters import MAX_SILENCE_DURATION

# htkModelParser = os.path.join(parentDir, 'htk2s3')
# sys.path.append(htkModelParser)

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)




class _LyricsWithModelsBase(object):
    '''
    lyrics with each Phoneme having a link to a model of class type htkModel from htkModelParser
    No handling of durationInMinUnit information. For it see Decoder.Decoder.decodeAudio 
    '''


    def __init__(self,  lyrics, htkParserOrFold, deviationInSec=0,  withPaddedSilence=True ):
        '''
        being  linked to models, allows expansion to network of states 
        '''
        
#       flag to add a state 'sp' with exponential disrib at begining and end  
        self.withPaddedSilence = withPaddedSilence
        
#         Lyrics.__init__(self, lyrics.listWords)
        self.lyrics = lyrics
        
        self.deviationInSec = deviationInSec
        # list of class type StateWithDur
        self.statesNetwork = []
        
        self.duratioInFramesSet = False

        self._linkToModels(htkParserOrFold)
        
        

    def _linkToModels(self, htkParserOrFold):
        # this is used for DNN trained. Link to models does not make sense for neural networks. 
        self._addPaddedSilencePhonemes()
    
    def _addPaddedSilencePhonemes(self):
        '''
        add a silent phoneme (neither a complete word, nor complete syllable) at the beginning and and of lyrics
        '''
       
        phonemeSp = PhonemeBase(SIL_TEXT)
        
        if self.withPaddedSilence:    
            
            phonemeSp.setIsLastInSyll(True)
            self.lyrics.phonemesNetwork.insert(0, phonemeSp)
            self.lyrics.phonemesNetwork.append(copy.deepcopy(phonemeSp))
    


    def _phonemes2stateNetwork(self):
        '''
        expand self.phonemeNetwork to self.statesNetwork
        assign phoneme a pointer <setNumFirstState> to its initial state in the state network (serves as link among the two)
        each state gets 1/n-th of total num of states. 
        '''
         
        
        self.statesNetwork = []
        stateCount = 0
        

        
        for phnIdx, phoneme in enumerate(self.lyrics.phonemesNetwork):
            
            
            # set number of first state
            phoneme.setNumFirstState(stateCount)
            
            deviation = -1
            
            if ParametersAlgo.WITH_DURATIONS:
                deviation = self.deviationInSec
                if not phoneme.isVowel(): # consonant
                        deviation = ParametersAlgo.CONSONANT_DURATION_DEVIATION
                
                distributionType='normal'
                ### for Makam, lyrics are read from score and sp is considered a consonant with short deviation. 
                ### only first and last phonemes (which are sp) will get padded silence 
                if (phnIdx == 0 or phnIdx == len(self.lyrics.phonemesNetwork)-1 ) and self.withPaddedSilence:
                    distributionType='exponential'
                
                if ParametersAlgo.FOR_JINGJU and phoneme.ID == 'sp':
                    distributionType='exponential'
            else:
                distributionType='exponential'

            ##### TODO: replace by simpleer logic: if it has 3 states, take index [1] if one take index 0, Note that sp has one
            stateIndices = list(range( phoneme.getNumStates()))   
#             if ParametersAlgo.ONLY_MIDDLE_STATE and len(phoneme.model.states) == 3: # take only middle state. 1 is middle in 0,1,2
#                      stateIndices = [1]
                    
            for idxState in stateIndices :
          
                currState = self._createStateWithDur(phoneme,  idxState, distributionType, deviation)
                self.statesNetwork.append(currState)
                stateCount += 1
        
                
    
    
    
    def printWordsAndStatesResutDurations(self, resultPath):
        '''
        debug word begining states
        '''
        
        if resultPath == None:
            logger.warn("printitg current lyrics with results not possible. resultPath is None. Make sure you decoded correctly! ")
            return
        
        for word_ in self.lyrics.listWords:
            print(word_ , ":") 
            for syllable_ in word_.syllables:
                for phoneme_ in syllable_.phonemes:
                    print("\t phoneme: " , phoneme_)
                    countPhonemeFirstState =  phoneme_.numFirstState

                    for nextState in range(phoneme_.getNumStates()):
                        print("\t\t state: {} durationInMinUnit (in Frames): {} DURATION RESULT: {}, t_end: {}".format(countPhonemeFirstState + nextState, 
                                                                                                self.statesNetwork[countPhonemeFirstState + nextState].durationInFrames,
                                                                                                 resultPath.durations[countPhonemeFirstState + nextState], 
                                                                                                 resultPath.endingTimes[countPhonemeFirstState + nextState]))

                    
    def  printWordsAndStates(self):
        '''
        word begining states
        NOTE: code redundant with method  printWordsAndStatesResutDurations() 
        TODO: to reduce code: use lyrics parsing . or like previous
        '''
        
        for word_ in self.lyrics.listWords:
            print(word_ , ":") 
            for syllable_ in word_.syllables:
                for phoneme_ in syllable_.phonemes:
                    print("\t phoneme: " , phoneme_)
                    countPhonemeFirstState =  phoneme_.numFirstState
                    
#                     print " \tdurationInMinUnit in min unit: {}".format(phoneme_.durationInMinUnit)
                    for nextState in range(phoneme_.getNumStates()):
                                    stateWithDur = self.statesNetwork[countPhonemeFirstState + nextState]
                                    try:
                                        currDurationInFrames = stateWithDur.durationInFrames
                                    except AttributeError:
                                        currDurationInFrames = 0
#                                     print "\t\t state: {} durationInMinUnit (in Frames): {}".format(countPhonemeFirstState + nextState, currDurationInFrames)
                                                                                                           
                
                



    def duration2numFrameDuration(self, observationFeatures, URI_audio,  tempoCoefficient = 1.0):
        '''

        scale the reference durations based on performance tempo  
        and
        set durations witin each syllable
        '''

        numFramesPerMinUnit = self.calc_scaling_factor(observationFeatures, URI_audio, tempoCoefficient)
        
        #  scale reference durations for each syllable based on tempo 
        for word_ in self.lyrics.listWords:
            for syllable_ in word_.syllables:
                
                if syllable_.durationInMinUnit == 0:  
                    logging.warning("syllable {} with duration = 0".format(syllable_))
                    syllable_.durationInMinUnit = 1 # workaround for syllables with 0 duration. better: if whole sentence unknown use withRules.
                
                numFramesInSyllable = round(float(syllable_.durationInMinUnit) * numFramesPerMinUnit) # scale 
                if numFramesInSyllable == 0.0:
                    sys.exit(" frames per syllable {} are 0.0. Check durationInMinUnit {} and numFramesPerMinUnit={}".format(syllable_.text, syllable_.durationInMinUnit,  numFramesPerMinUnit))
                    
                # TODO: set here syllables from score
                syllable_.setDurationInNumFrames(numFramesInSyllable)
        
        # set durations within each syllables
        self.lyrics.calcPhonemeDurs()
        
        self.duratioInFramesSet = True
        
    def calc_scaling_factor(self, observationFeatures, URI_audio, tempoCoefficient):
        '''
        calculate  scaling factor (numFramesPerMinUnit) for given audio URI_audio
        '''
        totalReferenceDur = self.lyrics.getTotalDuration() #         numFramesPerMinUnit   = float(len(observationFeatures) - 2 * AVRG_TIME_SIL * NUM_FRAMES_PERSECOND) / float(totalReferenceDur)
        lenObsFeatures = len(observationFeatures)
        numFramesPerMinUnit = float(tempoCoefficient * lenObsFeatures) / float(totalReferenceDur)
        logger.debug("numFramesPerMinUnit = {} for audiochunk {} ".format(numFramesPerMinUnit, URI_audio))
        return numFramesPerMinUnit
    
   
    
    
    def setPhonemeNumFrameDurs(self,  phoenemeAnnotaions):
        '''
        set durations in num frame durations read directly from textGrid. Used in oracle. 
        does not consider empty tokens (silences) at beginning and end, but reads sp tokens
        
        !! double check if annotated phoenemes  are the same as in lyrics !! 
        '''
        
        ##### put all annotated phonemes in queue
        queueAnnotationTokens = queue.Queue()
        for annoPhoneme in phoenemeAnnotaions:
            if annoPhoneme.ID == '':
                if ParametersAlgo.WITH_SHORT_PAUSES:
                    annoPhoneme.ID ='sp'
                else:
                    continue
        # WORKAROUND: needed for phonemes with strange names in Jingju. Uncomment only if need this  code WITH_ORACLE=1
#             self._renamePhonemeNames(annoPhoneme) 
            queueAnnotationTokens.put(annoPhoneme)
        # only first word
#         self.listWords = [self.listWords[0]]
        
        
        # used for debug tracking
        idxTotalPhonemeAnno = 0
        for word_ in self.lyrics.listWords:
            for syllable in word_.syllables:
#                 listDurations = []
#                 if syllable.text == 'REST' or syllable.text == '_SAZ_': # skip _SAZ_ because they are not annotated 
#                     continue
                for idx, phoneme_ in enumerate(syllable.phonemes): # current syllable
                    
                    idxTotalPhonemeAnno += idx
                    if queueAnnotationTokens.empty():
                        sys.exit("not enough phonemes in annotation at sylable {}".format(syllable.text))
                    phonemeAnno = queueAnnotationTokens.get()
                    logger.debug("phoneme from annotation {} and  phoneme from lyrics {} ".format(phonemeAnno.ID, phoneme_.ID ) )
                    if phonemeAnno.ID != phoneme_.ID:
                        sys.exit( " phoneme idx from annotation {} and  phoneme from lyrics  {} are  different".format( phonemeAnno.ID, phoneme_.ID ))

                    phoneme_.setBeginTs(float(phonemeAnno.beginTs))
                    currDur = computeDurationInFrames( phonemeAnno)
                    phoneme_.durationInNumFrames = currDur
        
        
        # expand to states       
        self._phonemes2stateNetwork()
#             self._phonemes2stateNetworkWeights()
        
        self.duratioInFramesSet = True    
        
    
    
    
    
    
    
            
            
     
     
    def _createStateWithDur(self, phoneme,  idxState, distributionType, deviationInSec):
        
        ''' 
        assign durationInMinUnit and name to each state.
        
        NOTE: class StateWithDur is not needed when WITH_DURATION = 0, could be replaced by the class State for simplicity of code, 
        but StateWithDur with wait prob is superset of State, so it serves the goal
        '''
        
        if distributionType == 'normal':
            currStateWithDur = StateWithDur( phoneme, idxState, distributionType, deviationInSec)
            try:
                dur = float(phoneme.durationInNumFrames) / float( phoneme.getNumStates() ) 
            except: 
                sys.exit('duration for phoneme  {} is not defined. Make sure to run src.align._LyricsWithModelsBase._LyricsWithModelsBase.duration2numFrameDuration first'.format(phoneme)) 
            if dur < 0:
                sys.exit("duration for phoneme {}={}. please decrease fixed consonant duration or make sure audio fragment is not too short".format(dur, phoneme.ID))
            currStateWithDur.setDurationInFrames(dur)
        
        elif distributionType == 'exponential':
            currStateWithDur = StateWithDur( phoneme, idxState, distributionType )
            currStateWithDur.setDurationInFrames( MAX_SILENCE_DURATION  * NUM_FRAMES_PERSECOND)
            
            
            ############# set wait prob
            if phoneme.isModelType == 'htk':
                transMatrix = phoneme.getTransMatrix()
                waitProb = transMatrix[idxState + 1, idxState + 1]
            else:
                waitProb = ParametersAlgo.GLOBAL_WAIT_PROB
            currStateWithDur.setWaitProb(waitProb)
        
        
        return currStateWithDur 
    

        
        
     
            
    
    def stateDurationInFrames2List(self):
        '''
        get Duration list for states ( in NumFrames)
        '''
        numFramesDurationsList = []
        
        if not self.duratioInFramesSet:
            logger.warn("no durationInMinUnit in frames set. Please call first duration2numFrameDuration()")
            return numFramesDurationsList
        
        
        for  i, stateWithDur_ in enumerate (self.statesNetwork):
            numFramesDurationsList.append(stateWithDur_.getDurationInFrames()) 
        
        return numFramesDurationsList
    
        
        
    def phonemeDurationsInFrames2List(self):
        '''
        get Duration list for phonemes (in NumFrames)
        '''
        
        listDurations = []
        totalDur = 0
        for phoneme_ in self.lyrics.phonemesNetwork:
            
            # print phoneme
            
            # get total dur of phoneme's states
            phonemeDurInFrames = 0
            countPhonemeFirstState= phoneme_.numFirstState
            
            for nextState in range(phoneme_.getNumStates()):
                        stateWithDur = self.statesNetwork[countPhonemeFirstState + nextState]
                        try:
                            phonemeDurInFrames += stateWithDur.durationInFrames
                        except AttributeError:
                            print("no durationInFrames Attribute for stateWithDur")
            
            
            listDurations.append(phonemeDurInFrames)
            totalDur += phonemeDurInFrames
        return listDurations
        
    def stateDurations2Network(self):
        '''
        make list with phoonemes and states (with so many repetition as durations)
        '''
        
        stateNetworkWithDurs = []
        if not self.duratioInFramesSet:
            logger.warn("no durationInMinUnit in frames set. Please call first duration2numFrameDuration()")
            return stateNetworkWithDurs
        
        
        for  i, stateWithDur_ in enumerate (self.statesNetwork):
            
            durInFrames = stateWithDur_.getDurationInFrames()
            for j in range(int(durInFrames)):
                 stateNetworkWithDurs.append(stateWithDur_)
        
        return stateNetworkWithDurs
     
        
    def printStates(self):
        '''
        debug: print states 
        '''
        
        
        for i, state_ in enumerate(self.statesNetwork):
                print("{} : {}".format(i, state_.display()))



def computeDurationInFrames(phonemeAnno):
        '''
        compute Duration from annotation token 
        '''
        durationInSec = float(phonemeAnno.endTs) - float(phonemeAnno.beginTs)
        durationInFrames = math.floor(durationInSec * NUM_FRAMES_PERSECOND)
        return durationInFrames

