'''
Created on Feb 24, 2016

@author: joro
'''
import sys
import numpy as np
import numpy.core.numeric
from src.hmm.continuous._ContinuousHMM import _ContinuousHMM
from src.align.ParametersAlgo import ParametersAlgo
from src.align._SyllableBase import SIL_TEXT
if ParametersAlgo.WITH_ORACLE_ONSETS != -1:
    from src.onsets.OnsetDetector import getDistFromEvent



class _HMM(_ContinuousHMM):
    '''
    classical Viterbi
    '''
    
    def __init__(self, statesNetwork):
    
#     def __init__(self,n,m,d=1,transMatrix=None,means=None,covars=None,w=None,pi=None,min_std=0.01,init_type='uniform',precision=numpy.double, verbose=False):
            '''
            See _ContinuousHMM constructor for more information
            '''
            pi = self._set_pi(statesNetwork)
             
            n = len(statesNetwork)
            min_std=0.01
            init_type='uniform'
            precision=numpy.double
            verbose = False 
            _ContinuousHMM.__init__(self, n, pi, min_std,init_type,precision,verbose) #@UndefinedVariable
    
            self.statesNetwork = statesNetwork
            
            self.transMatrix = constructTransMatrix(statesNetwork)


      
    def _set_pi(self,  statesSequence):

       
        numStates = len(statesSequence)
        
        # start probs :
        pi = numpy.zeros((numStates), dtype=numpy.double)
        
        # avoid log(0) 
        pi.fill(sys.float_info.min)
#          allow to start only at first state
        pi[0] = 1


#         pi[0] = 0.33
#         pi[1] = 0.33
#         pi[2] = 0.33
        
        # equal prob. for states to start
#         pi = numpy.ones( (numStates)) *(1.0/numStates)
#         np.savetxt('pi_umbrella_line.txt', pi)
                            
        return  pi    
        


    def viterbi_fast_forced(self):
        '''
        forced alignment. uses essentia
        '''
        import essentia.standard as es 

        esViterbi = es.Viterbi(forcedAlignment=1)
        
        trans_matrix_ = es.essentia.array(self.transMatrix) # should be in log domain
        B_map_ = es.essentia.array(self.B_map) # should be in log domain
        pi_ = es.essentia.array(self.pi)
        (phi_, psi_) = esViterbi(trans_matrix_, B_map_, pi_)
        self.phi = phi_.T
        self.psi = psi_.T
        return self.psi
    
    
    def viterbi_fast_pablo(self):
        '''
        A python version of essentia's algorithm
        this should yield ideally same results as viterbi_fast_forced 
        '''
                # init phi and psi at first time
        
        eps = np.finfo(float).eps
        
        n = len(self.transMatrix)
        obsSize = self.B_map.shape[1]
        lattProbs = np.empty([obsSize, n])
        lattPtrs = np.empty([obsSize, n])
    
        for j in range(n):
            currLogPi = np.log(self.pi[j] + eps)
            lattProbs[0][j] = currLogPi + self.B_map[j][0]
        
        # viterbi loop
        for t in range(1,obsSize):
            for j in range(n):
                sliceA = self.transMatrix[:,j]
                APlusPhi = np.add(lattProbs[t-1,:], sliceA)
                lattProbs[t][j] = np.max(APlusPhi)
                lattProbs[t][j] += self.B_map[j][t]
                lattPtrs[t][j] = np.argmax(APlusPhi)
        return lattProbs, lattPtrs
    
    
    def viterbi_fast_forced_python(self):
        '''
        forced alignment: considers only previous state in decision
        uses log prob.
        '''
        
        #   total likelihood matrix  
        obsSize = self.B_map.shape[1]

        self.phi = numpy.empty((obsSize,self.n),dtype=self.precision)
        self.phi.fill(-numpy.core.numeric.Infinity)
    
       
        # backpointer: from which prev. state
        self.psi = numpy.empty((obsSize, self.n), dtype=self.precision)
        self.psi.fill(-1) # in this context it it should not be 0, because it has a meaning - e.g. pointer to 0 state
        
        # init phi and psi at first time
        for j in range(self.n):
            currLogPi = numpy.log(self.pi[j])
            self.phi[0][j] = currLogPi + self.B_map[j][0]
        
        lenObs = numpy.shape(self.B_map)[1]
        
        # viterbi loop    
        for t in range(1,lenObs):
#             self.logger.debug("at time {} out of {}".format(t, lenObs ))
            
            for j in range(self.n):
                        fromState = j-2 # can skip a state
                      
                        if j == 0 or j==1:  # if beginning states, no skip state
                            fromState = 0
                            
                        sliceA = self.transMatrix[fromState:j+1,j]
                        APlusPhi = numpy.add(self.phi[t-1,fromState:j+1], sliceA) # add observation and transition likelihood
                        
                        # pick up maximmum prev. state  
                        self.phi[t][j] = numpy.max(APlusPhi) 
                        self.psi[t][j] = numpy.argmax(APlusPhi) + fromState

                        self.phi[t][j] += self.B_map[j][t] # sum likelihood

        
#         np.savetxt('persistent/phi_umbrella_line.txt', self.phi)
#         np.savetxt('persistent/psi_umbrella_line.txt', self.psi)            
        return self.psi 
   
    
    def viterbi_fast(self):
        '''
        basic viterbi, no forced alignment, with onsets
        @broken, not updated after refactoring
        '''
        
        # init phi and psi at first time
        for j in range(self.n):
            currLogPi = numpy.log(self.pi[j])
            self.phi[0][j] = currLogPi + self.B_map[j][0]
        
        # viterbi loop    
        lenObs = numpy.shape(self.B_map)[1]
        for t in range(1,lenObs):
            self.logger.debug("at time {} out of {}".format(t, lenObs ))
            for j in range(self.n):
#                 for i in xrange(self.n):
#                     if (delta[t][j] < delta[t-1][i]*self.transMatrix[i][j]):
#                         delta[t][j] = delta[t-1][i]*self.transMatrix[i][j]
                        
                        if self.noteOnsets[t]:
                            sliceA = self.transMatrixOnsets[:,j]
#                             print "at time {} using matrix for note Onset".format(t)
                        else:
                            sliceA = self.transMatrix[:,j]
                             
#                         print "shape transMatrix:" + str(self.transMatrix.shape)
#                         print "shape phi:" + str(self.phi.shape)
                        APlusPhi = numpy.add(self.phi[t-1,:], sliceA)
                        
                        self.phi[t][j] = numpy.max(APlusPhi)
                        self.phi[t][j] += self.B_map[j][t]

                        self.psi[t][j] = numpy.argmax(APlusPhi)
            ##### visualize each selected chunk
            tmpArray = numpy.zeros((1,self.psi.shape[1]))
            tmpArray[0,:] = self.psi[t,:]
#             visualizeMatrix(tmpArray)
                    
#         numpy.savetxt(PATH_LOGS + '/phi', self.phi)
#         numpy.savetxt( PATH_LOGS + '/psi', self.psi)
        return self.psi
       
       
    def visualize_trans_probs(self, lyricsWithModels, fromFrame, toFrame, from_phoneme, to_phoneme):
        '''
        forced alignment: considers only previous state in desicion
        '''
        
        import matplotlib
        lenObs = numpy.shape(self.B_map)[1]
        tmpOnsetProbArray = numpy.zeros((to_phoneme-from_phoneme + 1, lenObs)) 
        
        # viterbi loop    
#         for t in xrange(1,lenObs):
        for t in range(fromFrame, toFrame):
            self.logger.debug("at time {} out of {}".format(t, lenObs ))
            
            if ParametersAlgo.WITH_ORACLE_ONSETS == -1:
                    whichMatrix = -1 # last matrix with no onset
            else:
                    # distance of how many frames from closest onset
                    onsetDist, _ = getDistFromEvent( self.noteOnsets, t)
                    whichMatrix = min(ParametersAlgo.ONSET_SIGMA_IN_FRAMES + 1, onsetDist)
                    self.logger.debug( "which Matrix: " + str(whichMatrix) )
                    
            for j in range(from_phoneme, to_phoneme+1):
                        if j > 0:
                            a = self.transMatrices[whichMatrix][j-1,j]
                            tmpOnsetProbArray[j-from_phoneme, t] = a # because of indexing

                         
#             visualizeMatrix(tmpOnsetProbArray, 'titleName')

        matplotlib.rcParams['figure.figsize'] = (20, 8)
        visualizeMatrix(tmpOnsetProbArray[:,fromFrame:toFrame], '')
        
        ###### add vertical legend names
        statesNetworkNames  = []
        for i in range(from_phoneme,to_phoneme+1):
            stateWithDur = lyricsWithModels.statesNetwork[i]
            stateWithDurPrev = lyricsWithModels.statesNetwork[i - 1]
            statesNetworkNames.append("{} -> {}".format(stateWithDurPrev.phoneme.ID, stateWithDur.phoneme.ID))
            
        import matplotlib.pyplot as plt
        from numpy.core.numeric import arange
        plt.yticks(arange(len(statesNetworkNames)) , statesNetworkNames )
        plt.show()
        
def constructTransMatrix(statesNetwork):
    '''
    iterate over states and put their wait probs in a matrix 
    '''
    # just for initialization totalNumPhonemes
    totalNumStates = len(statesNetwork)
    if totalNumStates <= 0:
        sys.exit('lyrics are expanded to 0 states... ')
    transMAtrix = numpy.zeros((totalNumStates, totalNumStates), dtype=numpy.double)
#         transMAtrix.fill(0.1)
    
    for idxCurrState in range(totalNumStates):
         
        curr_state = statesNetwork[idxCurrState]
        
        
        if (idxCurrState+2) < transMAtrix.shape[1]: # MAIN CASE
       
                nextState = statesNetwork[idxCurrState+1]
                forwProb1, forwProb2 = define_forward_trans_probs(curr_state, nextState)
               
                while (forwProb1 + forwProb2 >= 1): # normalize
                   forwProb1 /= 2.0
                   forwProb2 /= 2.0
                
                ##### asign calculated probabilities
                transMAtrix[idxCurrState, idxCurrState] = 1 - forwProb1 - forwProb2 # waitProb = 1-forw-forw2
                transMAtrix[idxCurrState, idxCurrState + 1] = forwProb1
                transMAtrix[idxCurrState, idxCurrState + 2] = forwProb2  
                
                
        elif (idxCurrState+1) < transMAtrix.shape[1]: # SPECIAL CASE: two last states
                            
            transMAtrix[idxCurrState, idxCurrState] = curr_state.getWaitProb()
            transMAtrix[idxCurrState, idxCurrState+1] = 1 - curr_state.getWaitProb()
        
        else: #  SPECIAL CASE: at very last state
            
            transMAtrix[idxCurrState, idxCurrState] = curr_state.getWaitProb() # waitProb
        
    # avoid log(0) 
    indicesZero = numpy.where(transMAtrix==0)
    transMAtrix[indicesZero] = sys.float_info.min
    
    ###### normalize trans probs to sum to 1.
    import sklearn.preprocessing
    transMAtrix = sklearn.preprocessing.normalize(transMAtrix, axis=1, norm='l1')
    
     # do not rewrite in C++
#     if ParametersAlgo.VISUALIZE:  
#         figureTitle = "onsetDist = {}".format(onsetDist)  
#         visualizeTransMatrix(transMAtrix, figureTitle, lyricsWithModels.phonemesNetwork )
            
    return transMAtrix  



def define_forward_trans_probs(curr_state, nextState):
    '''
    defines transition probabilities in a way that silent pause (SIL_TEXT) could be skipped 
    '''
    if nextState.phoneme.ID == SIL_TEXT: # going to next phoneme=sp or skipping it is equaly likely
        forwProb1 = 1 - curr_state.getWaitProb() / 2.0
        forwProb2 = 1 - curr_state.getWaitProb() / 2.0
    else:
        forwProb1 = 1 - curr_state.getWaitProb()
        forwProb2 = 0 # no note onset and no silent token: use transition trained from data
    return forwProb1, forwProb2
               
