'''
Created on Nov 4, 2014

@author: joro
'''
import numpy
import sys
import logging

from src.align.Decoder import BACKTRACK_MARGIN_PERCENT 
#     set BACKTRACK_MARGIN_PERCENT to 0 to make backtracking only once from last state 

from src.align.ParametersAlgo import ParametersAlgo
from src.align.LyricsParsing import get_state_idx_word, getBoundaryFrames
from src.utilsLyrics.UtilzNumpy import map_span
logger = logging.getLogger(__name__)
logger.setLevel(ParametersAlgo.LOGGING_LEVEL)

HIGH_BOUND_SOURCE_SPAN = 0.5 # high cut-off of source probability. Decide empirically to cut-off high outliers
LOW_BOUND_TARGET_SPAN = 0.58 #  probability target lower bound 
HIGH_BOUND_TARGET_SPAN = 1.5 # #  probability target higher bound. Could be more than 1 to map better higher values to target range



class Path(object):
    '''
    Result path postprocessing
    '''


   
    def __init__(self, psiBackPointer = None, chiBackPointers = None):
        '''
        Constructor
        '''
        
        
        if  psiBackPointer is not None: # trigger backtracking if construcor called with phi back pointer 
            
            self.run_backtracking(psiBackPointer, chiBackPointers)
            
                ##########  calculate total phi for recording. Not needed,replaced by average of segments
#         numdecodedStates = len(self.indicesStateStarts) 
#         self.phi_total = self._calc_phi_segment(0, numdecodedStates - 1, 0, finalTime) # from last state and current final frame
        
     
    def run_backtracking(self,  psiBackPointer, chiBackPointer = None):
        '''
        run backtracking multiple times
        '''
        (totalTime, numStates) = numpy.shape(psiBackPointer) # infer from pointer matrix
        finalTime = totalTime - 1
        self.pathRaw = [1] # init path
        totalAllowedDevTime = totalTime - BACKTRACK_MARGIN_PERCENT * totalTime
        while self.pathRaw[0] != 0 and finalTime >= totalAllowedDevTime: # not reached first state
            '''
        decrease final time until reached first state (=0)
        '''
            logger.debug('backtracking from final time {}'.format(finalTime))
            if ParametersAlgo.WITH_DURATIONS:
                self.pathRaw = self._backtrackForcedDur(chiBackPointer, psiBackPointer, finalTime)
            else:
                self.pathRaw = self._backtrack(psiBackPointer, finalTime)
            self.path2stateIndices()
            finalTime = finalTime - 1 # decrement
        
    # final sanity check
        if self.pathRaw[0] != 0:
            sys.exit(' backtracking NOT completed! stopped because reached totalAllowedDevTime. Exiting...  {}'.format(totalAllowedDevTime))

            
    def setPathRaw(self, pathRaw):
        self.pathRaw = pathRaw
        if self.pathRaw[0] != 0:
            sys.exit('loaded path does not start form first state. Exiting...')
        self.path2stateIndices()
    
    def _backtrack(self, psiBackPointer,  finalTime):
        '''
        backtrack Viterbi starting from last state. no durations, standard viterbi
        '''
        
        totalTIme, numStates = numpy.shape(psiBackPointer)
        rawPath = numpy.zeros( (finalTime + 1), dtype=int )
        
        t = finalTime
        # start from last state
        currState = numStates - 1
        # start from state with biggest prob
#         currState = numpy.argmax(hmm.phi[finalTime,:])
        rawPath[finalTime] = currState
        
        while(t>0):
            # backpointer
            pointer = psiBackPointer[t, currState]
            if pointer == -1:
                sys.exit("at time {} the backpointer for state {} is not defined".format(t,currState))
            currState = int(pointer)
            rawPath[t-1] = currState
            ### update 
            t = t-1
    
        self.pathRaw = rawPath
        return rawPath
        
    
    def _backtrackForcedDur(self, chiBackPointers, psiBackPointer, finalTime):
        '''
        starts at last state. 
        finds path following back pointers
        '''
        
        self.durations = [] # detected durations
        self.endingTimes = [] # ending time for each state
        
        if chiBackPointers is None:
            sys.exit(chiBackPointers == 0)
        
        totalTIme, numStates = numpy.shape(psiBackPointer)
        rawPath = numpy.empty( (totalTIme), dtype=int )
        
        # put last state till end of path
        if finalTime < totalTIme - 1:
            rawPath[finalTime+1:totalTIme] = numStates - 1

        # termination: start at end state
        t = finalTime
        currState = numStates - 1
        duration = chiBackPointers[t,currState]

        
        # path backtrakcing. allows to 0 to be starting state, but not to go below 0 state
        while (t>duration and currState > 0):
            if duration <= 0:
                print("Backtracking error: duration for state {} is {}. Should be > 0".format(currState, duration))
                sys.exit()
            
            rawPath[int(t-duration)+1:int(t+1)] = currState
            
            # for DEBUG: track durations: 
            self.durations.append(duration)
            self.endingTimes.append(t)
            
            ###### increment
            # pointer of coming state
            currState = psiBackPointer[int(t), int(currState)]
            
            t = t - duration
            # sanity check. 
            if currState < 0:
                sys.exit("state {} at time {} < 0".format(currState,t))
            
            duration = chiBackPointers[int(t),int(currState)]
        # fill in with beginning state
        rawPath[0:int(t+1)] = currState
        
        # DEBUG: add last t
        self.durations.append(t)
        self.endingTimes.append(t)
        
        self.durations.reverse() 
        self.endingTimes.reverse()    
   
        return rawPath
    
    def path2stateIndices(self):
        '''
         indices in pathRaw where a new state starts. 
         the array index is the consequtive state count from sequence  
        '''
        self.indicesStateStarts = []
        currState = -1
        for i, p in enumerate(self.pathRaw):
            if p != currState:
              self.indicesStateStarts.append(i)
              currState = p
        ######### sanity check
        unique_states = set(self.pathRaw)
        if len(self.indicesStateStarts) != len(unique_states):
            sys.exit('unique states  not same number as new states start')
        
            
              

    
    def calc_phi_segments_lines(self, phi, lyricsWithModels):
        '''
        calculates the phi segments from the path corresponding to each line of the lyricsWithModels 
        '''
        
        phis_segments_for_lines = []
        
        i = 0
        phi_segment_min = 100
        phi_segment_max = -1
        while i < len(lyricsWithModels.lyrics.listWords):
            start_word_idx = i
            while i < len(lyricsWithModels.lyrics.listWords) and \
             not lyricsWithModels.lyrics.listWords[i].is_last_in_sentence(): # find end of next sentence
                i +=1;
            end_word_idx = i
            i +=1 # move to next sentence
            
            idx_begin_state, idx_end_state, begin_frame, end_frame = self.get_segment_indices(lyricsWithModels, start_word_idx, end_word_idx)
            phi_segment = self._calc_phi_segment(phi, idx_begin_state, idx_end_state, begin_frame, end_frame)
            
            phi_segment_min = min(phi_segment_min, phi_segment)
            phi_segment_max = max(phi_segment_max, phi_segment)
            
            phis_segments_for_lines.append(phi_segment)
        return phis_segments_for_lines
    
    def _calc_phi_segment(self, phi, idx_begin_state, idx_end_state, begin_frame, end_frame):
        '''
        calculate a phi segment for a sentence from start_word_idx to end_word_idx
        map to a new range that is between 0.55 and 1 to serve as confidence
        '''
        phi_segment_raw = self._extract_phi_segment(phi, end_frame, idx_end_state, begin_frame, idx_begin_state)
        num_frames = end_frame - begin_frame
        phi_segment_value = calc_phi_score(phi_segment_raw, num_frames)
        phi_segment_value = min(phi_segment_value, HIGH_BOUND_SOURCE_SPAN) # trim high-valued outliers that would skew negatively target time span  
        phi_segment_value_mapped = map_span(phi_segment_value, 0, HIGH_BOUND_SOURCE_SPAN, LOW_BOUND_TARGET_SPAN, HIGH_BOUND_TARGET_SPAN)
        phi_segment_value_mapped = min(phi_segment_value_mapped, 0.99) # trim target value be in probability range
        return phi_segment_value_mapped
        
    def _extract_phi_segment(self, phi, end_time, end_state_idx, start_time=None,  start_state_idx=None ):
        '''
        extract the phi (cumulative likelihood) for a segment of the path
        '''
        if start_time == None and start_state_idx == None:
            phi_segment = phi[end_time, end_state_idx]
        else:
            phi_stsart = phi[start_time, start_state_idx]
            phi_end = phi[end_time, end_state_idx]
            phi_segment = phi_end - phi_stsart
        return phi_segment # scale by a number to get bigger than -708, otherwise np.exp(phi) returns 0
 

    
    
    def get_segment_indices(self, lyricsWithModels, idx_from_word, idx_to_word):
        '''
        extract indices for a segment of a path for given subset of words from  given lyricsWithModels. 
        If from_word is first word, returns the very beginning of the phonemeNetwork (there could be silent phoneme prepended before first word)
        Analogously to last word, returns last phoneme
        
        Parameters
        ----------------
        
        lyricsWithModels: 
            the given input lyrics
            
        Returns
        ----------------
        (x,y) of start of segment from path and (x,y) of end of segment 
         
        '''
        if idx_from_word == 0: # at first word, take first phoneme
            idx_from_state = lyricsWithModels.lyrics.phonemesNetwork[0].numFirstState
        else:
            from_word = lyricsWithModels.lyrics.listWords[idx_from_word]
            idx_from_state, _ = get_state_idx_word(from_word, lyricsWithModels.statesNetwork )

        if idx_to_word == -1 or idx_to_word == len(lyricsWithModels.lyrics.listWords) - 1: # at last word, take last phoneme
            last_phoneme = lyricsWithModels.lyrics.phonemesNetwork[-1]
            idx_to_state = last_phoneme.numFirstState + last_phoneme.getNumStates() - 1 
        else:
            to_word = lyricsWithModels.lyrics.listWords[idx_to_word]
            _, idx_to_state = get_state_idx_word(to_word, lyricsWithModels.statesNetwork )
            
        
        from_frame, to_frame = getBoundaryFrames(idx_from_state, idx_to_state, self)
        return idx_from_state, idx_to_state, from_frame, to_frame
        
        
    
    def printDurations(self):
        '''
        DEBUG: print durations
        ''' 
        print(self.durations)
        
def calc_phi_score(phi_raw, num_time_frames):
    '''
    calc phi segment averaged over number of processed time frames and convert from log domain 
    '''
    phi_avrg =  phi_raw  / float(num_time_frames)
    if phi_avrg < numpy.log(numpy.finfo(numpy.float64).tiny):
        logger.warning('very low total phi, taking minimal possible value instead to avoid underflow')
        phi_avrg = numpy.log(numpy.finfo(numpy.float64).tiny)        
#     phi_averaged = numpy.power(numpy.exp(phi_raw), 1. / float(num_time_frames) ) # take geometric mean over number of states
    return numpy.exp(phi_avrg)               
    