# -*- coding: utf-8 -*-

'''
Created on Dec 16, 2014
Utility class: logic for parsing statesNetwork, phoeneNetwork  
@author: joro
'''
import sys
import logging
import os

from .Constants import NUM_FRAMES_PERSECOND, NUMSTATES_SIL, NUMSTATES_PHONEME

from .ParametersAlgo import ParametersAlgo
from src.align._SyllableBase import SIL_TEXT
if ParametersAlgo.FOR_MAKAM:
    from src.for_makam.PhonemeMakam import PhonemeMakam
from src.utilsLyrics.Utilz import frameNumberToTs
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)
    



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)
    
def expand_path_to_wordList (lyricsWithModels, path, func):
    '''
    expand path to words and corresponding timestamps
    @param path stands for path or statesNetwork
    '''

    wordList = []
       
    for word_ in lyricsWithModels.lyrics.listWords:
        if len(word_.syllables) == 0:
            sys.exit('word {} has 0 syllables'.format(word_))
        countFirstState, countLastState = get_state_idx_word(word_, lyricsWithModels.statesNetwork )

        startNoteNumber = word_.syllables[0].noteNum
        
        currWord_and_ts, totalDuration = func( word_.text, countFirstState, countLastState, path, 'dummy')
        
#         if currWord_and_ts[2] !=  '_SAZ_':
        wordList.append( currWord_and_ts)
    return wordList

def token_list_to_line_ts( lyrics, detected_token_list):
    '''
    parse the list of word tokens. add a ts for each word at the beginning of a line
    '''
    idx_begin_line = 0
    lines_begin_ts = []
    for lyrics_line in lyrics.lyrics_lines:
        lines_begin_ts.append(detected_token_list[idx_begin_line][0])
        idx_begin_line += len(lyrics_line.listWords)
    return lines_begin_ts  

def get_state_idx_word(word_, states_network):
    '''
    retrieve the indices of the first state (phoneme) and the last state(phoneme) of a given word
    '''
    countFirstState = word_.syllables[0].phonemes[0].numFirstState
# word ends at first state of sp phonemene (assume it is sp)
    lastSyll = word_.syllables[-1]
    lastPhoneme = word_.syllables[-1].phonemes[-1]
    countLastState = get_idx_last_state_word(states_network, word_, lastSyll, lastPhoneme)
    return countFirstState, countLastState

def get_idx_last_state_word(states_network, word_, lastSyll, lastPhoneme):
    '''
    retrieve the index of the last state (phoneme) in a word  
    '''
    if lastSyll.hasShortPauseAtEnd:
        if lastPhoneme.ID != SIL_TEXT:  # sanity check that last phoneme is sp
            msg = ' \n last state for word {} is not sp. Sorry - not implemented.'.format(word_.text)
            raise NotImplementedError(msg)
        countLastState = lastPhoneme.numFirstState # counter before sp 
    else:
        countLastState_ = lastPhoneme.numFirstState + lastPhoneme.getNumStates() - 1
        countLastState = min(countLastState_, len(states_network) - 1) # make sure not outside of state network
        
    return countLastState



def expand_path_to_SyllableList (lyricsWithModels, path, totalDuration, func):
    '''
    expand @path to words and corresponding timestamps
    @param path stands for path or statesNetwork
    '''

#     syllableList = []
    wordList = []

       
    for word_ in lyricsWithModels.lyrics.listWords:
        
        currWordArray = []
        lastSyll = word_.syllables[-1]
        for syllable_ in word_.syllables:
            
            countFirstState = syllable_.phonemes[0].numFirstState
            lastPhoneme = syllable_.phonemes[-1]
            countLastState = lastPhoneme.numFirstState + lastPhoneme.getNumStates()
            
            if syllable_ == lastSyll:
                countLastState = get_idx_last_state_word(lyricsWithModels.statesNetwork, word_, lastSyll, lastPhoneme)
            
            currSyllAndTs, totalDuration = func( syllable_.text, countFirstState, countLastState, path, totalDuration)
            
            
            currWordArray.append( currSyllAndTs)
        
#         if currWordArray[0][2] !=  '_SAZ_': # exclude _SAZ_ syllables
        wordList.append(currWordArray)  
        
            
    return wordList

def expand_path_to_phonemes_list(statesNetwork, path, func):
        
        detectedTokenList = []
        for i, idx_start in enumerate(path.indicesStateStarts):
            
            idx_first_state = path.pathRaw[idx_start]
            if i == len(path.indicesStateStarts) - 1: # at the end, take last state idx from path
                idx_last_state = path.pathRaw[-1]
            else:
                idx_next_first_states = path.indicesStateStarts[i + 1]
                idx_last_state = path.pathRaw[idx_next_first_states]
            
            state = statesNetwork[idx_first_state]
            detectedPhoneme, _ = func( state.phoneme.ID, idx_first_state, idx_last_state, path, use_end_ts=True)
            
            detectedTokenList.append(detectedPhoneme)
        
        return detectedTokenList
    
    






def _constructTimeStampsForTokenDetected(  text, countFirstState, countLastState, path, use_end_ts=False):
        '''
        helper method. timestamps of detected word/syllable , read frames from path
        '''
        currTokenBeginFrame, currTokenEndFrame = getBoundaryFrames(countFirstState, countLastState, path)    
        
        startTs = frameNumberToTs(currTokenBeginFrame)
        if use_end_ts:
            endTs = frameNumberToTs(currTokenEndFrame)
            detected_token = [startTs, endTs, text]
        else:
            detected_token = [startTs, text]
#         print detected_token
        dummy = -1
        return detected_token, dummy



def getBoundaryFrames(countFirstState, countLastState, path):
    '''
    get indices of frames
    searches in the path of states, but only the indices where new states start
    '''
    if not hasattr(path, 'indicesStateStarts'):
        sys.exit('method  path.path2stateIndices() has to be run first  ')
        
    i = 0
    while countFirstState > path.pathRaw[path.indicesStateStarts[i]]:
        i += 1
    
    currWordBeginFrame = path.indicesStateStarts[i]
    
   
    while i < len(path.indicesStateStarts) and countLastState > path.pathRaw[path.indicesStateStarts[i]]:
        i += 1
    if i == len(path.indicesStateStarts): # last state has no new index, so just take last frame
        currWordEndFrame = len(path.pathRaw) -1
    else:
        currWordEndFrame = path.indicesStateStarts[i]
    
#     currWordBeginFrame = path.indicesStateStarts[countFirstState]
#     currWordEndFrame = path.indicesStateStarts[countLastState]
    
    return currWordBeginFrame, currWordEndFrame



def _findBeginEndIndices(lowLevelTokensList, lowerLevelTokenPointer, highLevelBeginTs, highLevelEndTs, highLevel, durationsList=None):
    ''' 
    find indices of lower level tier whihc align with indices of highLevel tier
    @return: fromLowLevelTokenIdx, toLowLevelTokenIdx
    @param lowerLevelTokenPointer: being updated, and returned 
    '''
    if durationsList != None:
        if len(durationsList) != len(lowLevelTokensList):
            sys.exit(" len(durationsList) {} != lowLevelTokensList {} ".format(len(durationsList), len(lowLevelTokensList)))
    
    currSentenceSyllablesLIst = []
    
    
    while lowLevelTokensList[lowerLevelTokenPointer][0] < highLevelBeginTs: # search for beginning
        lowerLevelTokenPointer += 1
    
    currTokenBegin = lowLevelTokensList[lowerLevelTokenPointer][0]
    if not currTokenBegin == highLevelBeginTs: # start Ts has to be aligned
        logging.warning("token of lower layer has starting time {}, but expected {} from higher layer ".format(currTokenBegin, highLevelBeginTs))
    fromLowLevelTokenIdx = lowerLevelTokenPointer
    
    while lowerLevelTokenPointer < len(lowLevelTokensList) and float(lowLevelTokensList[lowerLevelTokenPointer][1]) <= highLevelEndTs: # syllables in currSentence
        lowerLevelTokenPointer += 1
    
    currTokenEnd = lowLevelTokensList[lowerLevelTokenPointer - 1][1]
    if not currTokenEnd == highLevelEndTs: # end Ts has to be aligned
        logging.warning(" token of lower layer has ending time {}, but expected {} from higher layer ".format(currTokenEnd, highLevelEndTs))
    toLowLevelTokenIdx = lowerLevelTokenPointer - 1
    return  fromLowLevelTokenIdx, toLowLevelTokenIdx, lowerLevelTokenPointer, currSentenceSyllablesLIst



  
def stripPunctuationSigns(string_):
    isEndOfSentence = False
    if string_.endswith('\u3002') or string_.endswith('\uff0c') \
             or string_.endswith('Ôºü') or string_.endswith('ÔºÅ') or string_.endswith('Ôºö') \
             or string_.endswith(':') or string_.endswith(',') : # syllable at end of line/section
                string_  = string_.replace('\u3002', '') # comma 
                string_  = string_.replace(',','')
                string_  = string_.replace('\uff0c', '') # point
                string_  = string_.replace('Ôºü', '')
                string_  = string_.replace('ÔºÅ', '')
                string_  = string_.replace('Ôºö', '')
                string_  = string_.replace(':', '')
                                
                isEndOfSentence = True
    string_ = string_.strip()
    return isEndOfSentence, string_


def phonemeTokens2Classes( phonemeTokensAnno):
    phonemesAnnoList = []
    for phonemeAnno in phonemeTokensAnno:
        currPhn = PhonemeMakam(phonemeAnno[2].strip())
        currPhn.setBeginTs(phonemeAnno[0])
        currPhn.setEndTs(phonemeAnno[1])
        phonemesAnnoList.append(currPhn)
    
    return phonemesAnnoList


def _constructTimeStampsForToken(  text, startNoteNumber, countFirstState, countLastState, statesNetwork, totalDuration):
        '''
        helper method. timestamps for word/syllable based on durations read from score 
        '''
        
        currWordBeginFrame = totalDuration
        for currState in range(countFirstState, countLastState + 1):                 
            totalDuration += statesNetwork[currState].getDurationInFrames()
        currWordEndFrame = totalDuration
        
            
    # timestamp:
        
        
        startTs = float(currWordBeginFrame) / NUM_FRAMES_PERSECOND
        endTs = float(currWordEndFrame) / NUM_FRAMES_PERSECOND
        
        detectedWord = [startTs, endTs, text , startNoteNumber]
#         print detectedWord
        
        return detectedWord, totalDuration 

        
    
def testT(lyricsWithModels):
        '''
        parsing of words template function 
        '''
    
        indicesBeginWords = []
        
        currBeginIndex = NUMSTATES_SIL 
        for word_ in lyricsWithModels.listWords:
            
#             indicesBeginWords.append( (currBeginIndex, word_.text) )
            indicesBeginWords.append( currBeginIndex )

            wordTotalDur = 0 
            for syllable_ in word_.syllables:
                for phoneme_ in syllable_.phonemes:
                    currDuration = NUMSTATES_PHONEME * phoneme_.getDurationInMinUnit()
                    wordTotalDur = wordTotalDur + currDuration  
            
            currBeginIndex  = currBeginIndex + wordTotalDur
        
        # last word sil
        indicesBeginWords.append( currBeginIndex )

        
        return  indicesBeginWords  