'''
Created on Nov 12, 2012

@author: GuyZ
'''

import numpy
import numpy as np
import os
import sys
import logging

from src.align.ParametersAlgo import ParametersAlgo
from src.utilsLyrics.Utilz import tsToFrameNumber
from src.align._SyllableBase import SIL_TEXT
import time
# from sklearn.utils.extmath import logsumexp

parentDir = os.path.abspath(  os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir ) )
hmmDir = os.path.join(parentDir, 'HMM/hmm')
if hmmDir not in sys.path: sys.path.append(parentDir)

from src.hmm._BaseHMM import _BaseHMM



from src.utilsLyrics.Utilz import writeListOfListToTextFile



# to replace 0: avoid log(0) = -inf. -Inf + p(d) makes useless the effect of  p(d)
MINIMAL_PROB = sys.float_info.min



class _ContinuousHMM(_BaseHMM):
    '''
    transMatrix Continuous HMM - This is a base class implementation for HMMs with
    mixtures. transMatrix mixture is a weighted sum of several continuous distributions,
    which can therefore create a more flexible general PDF for each hidden state.
    
    This class can be derived, but should not be used directly. Deriving classes
    should generally only implement the PDF function of the mixtures.
    
    Model attributes:
    - n            number of hidden states
 
    - transMatrix            hidden states transition probability matrix ([NxN] numpy array)

    - pi           initial state's PMF ([N] numpy array).
    
    Additional attributes:
    - min_std      used to create a covariance prior to prevent the covariances matrices from underflowing
    - precision    a numpy element size denoting the precision
    - verbose      a flag for printing progress information, mainly when learning
    '''

    def __init__(self,n, pi=None,min_std=0.01,init_type='uniform',precision=numpy.double,verbose=False):
        '''
        Construct a new Continuous HMM.
        In order to initialize the models_makam with custom parameters,
        pass values for (transMatrix,means,covars,w,pi), and set the init_type to 'user'.
        
        Normal initialization uses a uniform distribution for all probablities,
        and is not recommended.
        '''
        _BaseHMM.__init__(self,n,precision,verbose) #@UndefinedVariable
        
        self.pi = pi

        self.min_std = min_std

#         self.reset(init_type=init_type)
        
        '''
        flag to load some decoding info from cached files, for example bMap and durationLookup table . 
        makes decoding faster 
        '''
        self.usePersistentFiles = False
        self.logger = logging.getLogger(__name__)
        # other logger set in decoder 
        loggingLevel = ParametersAlgo.LOGGING_LEVEL
#         loggingLevel = logging.INFO
#         loggingLevel = logging.WARNING

        self.logger.setLevel(loggingLevel)
        


    def set_PPG_filename(self, URI_bmap):
        self.PATH_BMAP = URI_bmap

    def setNonVocal(self, list_non_vocal_intervals):
        self.list_non_vocal_intervals = list_non_vocal_intervals     
    
    def reset(self,init_type='uniform'):
        '''
        If required, initalize the models_makam parameters according the selected policy
        '''        
        if init_type == 'uniform':
            self.pi = numpy.ones( (self.n), dtype=self.precision) *(1.0/self.n)
            self.transMatrix = numpy.ones( (self.n,self.n), dtype=self.precision)*(1.0/self.n)
            self.w = numpy.ones( (self.n,self.m), dtype=self.precision)*(1.0/self.m)            
            self.means = numpy.zeros( (self.n,self.m,self.d), dtype=self.precision)
            self.covars = [[ numpy.matrix(numpy.ones((self.d,self.d), dtype=self.precision)) for j in range(self.m)] for i in range(self.n)]
        elif init_type == 'user':
            # if the user provided a 4-d array as the covars, replace it with a 2-d array of numpy matrices.
            covars_tmp = [[ numpy.matrix(numpy.ones((self.d,self.d), dtype=self.precision)) for j in range(self.m)] for i in range(self.n)]
            for i in range(self.n):
                for j in range(self.m):
                    if type(self.covars[i][j]) is numpy.ndarray:
                        covars_tmp[i][j] = numpy.matrix(self.covars[i][j])
                    else:
                        covars_tmp[i][j] = self.covars[i][j]
            self.covars = covars_tmp
    
    def get_Indices_nonVocal_states(self):
        '''
        return indices for non-vocal states
        '''
        indices = []
        for currIdx, stateWithDur in enumerate(self.statesNetwork):
            if stateWithDur.phoneme.ID == SIL_TEXT: # phoneme for silence used as placeholder for non-vocal states
                indices.append(currIdx)
        return indices
    
    def _mapBStub(self, lenFeatureVectors):
        '''
        for sanity check all probs set to 1
        '''
        self.B_map = numpy.zeros( (self.n, lenFeatureVectors), dtype=self.precision)
        self.B_map.fill(1)
        self._addNonPossibleObs()
        self.B_map = numpy.log( self.B_map) 
        
    
    def _mapBOracle(self,  lyricsWithModelsOracle, lenFeatureVectors, fromTs):
        '''
        loop though phoneme states from  lyricsWithModelsOracle. 
        For each one, for the frames of its duration assign 1 in B_map and
         
        @param lyricsWithModelsOracle - lyrics read from annotation ground truth
        @param fromTs - time to start at
        '''
        
        # init matrix to be zero
        self.B_map = numpy.zeros( (self.n, lenFeatureVectors), dtype=self.precision)
        self.B_map.fill(MINIMAL_PROB)
#         firstPhoneme = lyricsWithModelsOracle.phonemesNetwork[0]
#         offSet = firstPhoneme.beginTs - fromTs
#         import math
#         startFrameNumber =  int(math.floor(offSet * NUMFRAMESPERSEC)) 

        next_sane_start_frame = 0
        for idx, state_ in enumerate(lyricsWithModelsOracle.statesNetwork): # only for ONLY_MIDDLE_PHONEME = True
        
            phoneme_  = state_.phoneme
            startFrameNumber = tsToFrameNumber(phoneme_.beginTs - fromTs)

            self.logger.debug("phoneme: {} with start dur: {} and duration: {}".format( phoneme_.ID, startFrameNumber, phoneme_.durationInNumFrames ))
           
            finalDurInFrames = startFrameNumber + state_.getDurationInFrames()
            startFrameNumber = max(next_sane_start_frame, startFrameNumber)  # make sure it does not start at same frame
            self.B_map[idx, startFrameNumber: finalDurInFrames+1 ] = 1
            next_sane_start_frame =  finalDurInFrames+1 
            #TODO: silence at beginning and end
        
        self._addNonPossibleObs()
        self.B_map = numpy.log( self.B_map)  # go to log domain
        self._normalizeBByMax()
        
    
    def _addNonPossibleObs(self, inLogDomain=False):
        '''
        a sanity step: 
        not possible to go in bottom left corner, because of forced alignment, so put zeros in there 
        do before log numpy
        '''
        upper = np.triu(self.B_map)
        indicesZero = np.where(upper==0)
        if inLogDomain:
            self.B_map[indicesZero] = numpy.log(MINIMAL_PROB)
        else:
            self.B_map[indicesZero] = MINIMAL_PROB
        
        
    def _mapB(self, features):    
        
        '''
        Required implementation for _mapB. Refer to _BaseHMM for more details.
        with non-vocal
        '''
        
        time0 = time.time()
        self.B_map = numpy.zeros( (self.n,len(features)), dtype=self.precision)
         
        for j in range(self.n): ######## for each state
            ProbsForj = self._pdfAllFeatures(features,j)
            
# normalize  probs for each state to sum to 1 (in log domain)
#             sumLogLiks = logsumexp(ProbsForj)
#             ProbsForj -= sumLogLiks
            self.B_map[j,:] = ProbsForj
        
        time1 = time.time()
        self.logger.debug(" stacking probabilities in observation matrix : {} seconds".format(time1-time0) )
         
        #### VOCAL NOVOCAL : do not reimplement     
#         self.modify_likelihoods_for_nonvocal_probs()
        self.modify_likelihoods_for_nonvocal_intervals()
        
        self._addNonPossibleObs(inLogDomain=False)
        self._normalizeBByMax(inLogDomain=False)
#         cutOffHistogram(self.B_map, ParametersAlgo.CUTOFF_BIN_OBS_PROBS)
        time2 = time.time()
        self.logger.debug(" normalizing observation probabilities: {} seconds".format(time2-time1) )


  
    def modify_likelihoods_for_nonvocal_probs(self):
        '''
        make silent states be with  likelihood = 1  to regions with probability of being non-vocal > threshold
        list_non_vocal_intervals are in fact vocal probs
        '''
        indicesSilent = self.get_Indices_nonVocal_states() # get the indices of all states that are non-vocal in the phoneme Network
         
        # assign 1-s to non-vocal states
#         inputFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentation/data/laoshengxipi02.wav'
#         detectedSegments, outputFile, windowLen = doitSegmentVJP(inputFile)
        
        THRESHOLD = 0.55 
        # if listNonVocalNotdefinednot defined
        if hasattr(self, 'list_non_vocal_intervals'):
            for idx, point in enumerate(self.list_non_vocal_intervals):         # for each non-vocal region
                if point > THRESHOLD and idx <self.B_map.shape[1]:
                    self.B_map[:,idx] = numpy.log(MINIMAL_PROB)
                    self.B_map[numpy.array([indicesSilent]),idx] =  numpy.log(1)
    #             print "start: " + str(segStart[i]) + "\tend: " + str((segStart[i] + segDuration[i])) + "\t" + str(segPred[i]) 
            

    def modify_likelihoods_for_nonvocal_intervals(self):
        '''
        make silent states be with  likelihood = 1  to regions with probability of being non-vocal > threshold
        '''
        indices_non_vocal_states = self.get_Indices_nonVocal_states() # get the indices of all states that are non-vocal in the phoneme Network
         
        # assign 1-s to non-vocal states
        
        # if listNonVocalNotdefinednot defined
        if hasattr(self, 'list_non_vocal_intervals'):
            for nonVocalFrag in self.list_non_vocal_intervals:         # for each non-vocal region
              
                
                startFrame = tsToFrameNumber(nonVocalFrag[0])
                endFrame = tsToFrameNumber(nonVocalFrag[1])
                #### hard threshold: set obs.prob of vov-vocal states to 1, the rest to zero.  
                self.B_map[:,startFrame:endFrame+1] =  MINIMAL_PROB
                self.B_map[numpy.array([indices_non_vocal_states]),startFrame:endFrame+1] =  1

    #             print "start: " + str(segStart[i]) + "\tend: " + str((segStart[i] + segDuration[i])) + "\t" + str(segPred[i]) 
            
    

    
    
    def _mapB_OLD(self, observations):
        '''
        @deprecated
        Required implementation for _mapB. Refer to _BaseHMM for more details.
        This method highly optimizes the running time, since all PDF calculations
        are done here once in each training iteration.
        
        - self.Bmix_map - computesand maps Bjm(Ot) to Bjm(t).
        log precomputed
        '''   
#         return
        
        if self.usePersistentFiles and os.path.exists(self.PATH_BMAP):
            
            self.logger.info("loading probs all observations from {}".format(self.PATH_BMAP))
 
            self.B_map = numpy.loadtxt(self.PATH_BMAP)
            # check length
            if self.B_map.shape[1]  == len(observations)  and self.B_map.shape[0] == self.n:
#                 sys.exit('{} does not store all feature vectors. delete it and generate them again'.format(self.PATH_BMAP))
                
                self.B_map = numpy.log( self.B_map)
                return     
            else:
                self.logger.info("file {} found, but has not the expected num of states {} or observations {}".format(self.PATH_BMAP, self.n, len(observations)) )
       
        self.B_map = numpy.zeros( (self.n,len(observations)), dtype=self.precision)
        self.Bmix_map = numpy.zeros( (self.n,self.m,len(observations)), dtype=self.precision)
        
        for j in range(self.n):
            for t in range(len(observations)):
                self.logger.debug("at calcbjt at state {} and time {}...\n".format(j, t))
                lik = self._calcbjt(j, t, observations[t])
              
                if lik == 0: 
                    self.logger.debug("obs likelihood at time {} for state {} = 0. Repair by adding {}".format(t,j, MINIMAL_PROB))
                    lik = MINIMAL_PROB
                  
                self.B_map[j,t] = lik
  

        # normalize over states
        for t in range(len(observations)):
             self.B_map[:,t] = _normalize(self.B_map[:,t])
             self.logger.debug("sum={} at time {}".format(sum(self.B_map[:,t]), t))
             
        if self.usePersistentFiles:        
            writeListOfListToTextFile(self.B_map, None , self.PATH_BMAP)                 

        self.B_map = numpy.log( self.B_map)
                
    """
    b[j][Ot] = sum(1...M)w[j][m]*b[j][m][Ot]
    Returns b[j][Ot] based on the current models_makam parameters (means, covars, weights) for the mixtures.
    - j - state
    - Ot - the current observation
    Note: there's no need to get the observation itself as it has been used for calculation before.
    """    
    def _calcbjt(self,j,t,Ot):
        '''
        Helper method to compute Bj(Ot) = sum(1...M){Wjm*Bjm(Ot)}
        '''
        
        bjt = 0
        for m in range(self.m):
            
            mean = self.means[j][m]
            covar = self.covars[j][m]
            
            self.Bmix_map[j][m][t] = self._pdf(Ot, mean, covar)
            bjt += (self.w[j][m]*self.Bmix_map[j][m][t])
        return bjt
        
    def _calcgammamix(self,alpha,beta,observations):
        '''
        Calculates 'gamma_mix'.
        
        Gamma_mix is a (TxNxK) numpy array, where gamma_mix[t][i][m] = the probability of being
        in state 'i' at time 't' with mixture 'm' given the full observation sequence.
        '''        
        gamma_mix = numpy.zeros((len(observations),self.n,self.m),dtype=self.precision)
        
        for t in range(len(observations)):
            for j in range(self.n):
                for m in range(self.m):
                    alphabeta = 0.0
                    for jj in range(self.n):
                        alphabeta += alpha[t][jj]*beta[t][jj]
                    comp1 = (alpha[t][j]*beta[t][j]) / alphabeta
                    
                    bjk_sum = 0.0
                    for k in range(self.m):
                        bjk_sum += (self.w[j][k]*self.Bmix_map[j][k][t])
                    comp2 = (self.w[j][m]*self.Bmix_map[j][m][t])/bjk_sum
                    
                    gamma_mix[t][j][m] = comp1*comp2
        
        return gamma_mix
    
    def _updatemodel(self,new_model):
        '''
        Required extension of _updatemodel. Adds 'w', 'means', 'covars',
        which holds the in-state information. Specfically, the parameters
        of the different mixtures.
        '''        
        _BaseHMM._updatemodel(self,new_model) #@UndefinedVariable
        
        self.w = new_model['w']
        self.means = new_model['means']
        self.covars = new_model['covars']
        
    def _calcstats(self,observations):
        '''
        Extension of the original method so that it includes the computation
        of 'gamma_mix' stat.
        '''
        stats = _BaseHMM._calcstats(self,observations) #@UndefinedVariable
        stats['gamma_mix'] = self._calcgammamix(stats['alpha'],stats['beta'],observations)

        return stats
    
    
    def _reestimateMixtures(self,observations,gamma_mix):
        '''
        Helper method that performs the Baum-Welch 'M' step
        for the mixture parameters - 'w', 'means', 'covars'.
        '''        
        w_new = numpy.zeros( (self.n,self.m), dtype=self.precision)
        means_new = numpy.zeros( (self.n,self.m,self.d), dtype=self.precision)
        covars_new = [[ numpy.matrix(numpy.zeros((self.d,self.d), dtype=self.precision)) for j in range(self.m)] for i in range(self.n)]
        
        for j in range(self.n):
            for m in range(self.m):
                numer = 0.0
                denom = 0.0                
                for t in range(len(observations)):
                    for k in range(self.m):
                        denom += (self._eta(t,len(observations)-1)*gamma_mix[t][j][k])
                    numer += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m])
                w_new[j][m] = numer/denom
            w_new[j] = self._normalize(w_new[j])
                
        for j in range(self.n):
            for m in range(self.m):
                numer = numpy.zeros( (self.d), dtype=self.precision)
                denom = numpy.zeros( (self.d), dtype=self.precision)
                for t in range(len(observations)):
                    numer += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m]*observations[t])
                    denom += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m])
                means_new[j][m] = numer/denom
                
        cov_prior = [[ numpy.matrix(self.min_std*numpy.eye((self.d), dtype=self.precision)) for j in range(self.m)] for i in range(self.n)]
        for j in range(self.n):
            for m in range(self.m):
                numer = numpy.matrix(numpy.zeros( (self.d,self.d), dtype=self.precision))
                denom = numpy.matrix(numpy.zeros( (self.d,self.d), dtype=self.precision))
                for t in range(len(observations)):
                    vector_as_mat = numpy.matrix( (observations[t]-self.means[j][m]), dtype=self.precision )
                    numer += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m]*numpy.dot( vector_as_mat.T, vector_as_mat))
                    denom += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m])
                covars_new[j][m] = numer/denom
                covars_new[j][m] = covars_new[j][m] + cov_prior[j][m]               
        
        return w_new, means_new, covars_new
    



    def _normalizeBByMax(self, inLogDomain=False):
        '''
        Divide them by max in array. goal is to the decrease chance of underflow

        divide by max value. calculation done in log domain or non-log domain
        '''
        self.logger.debug("normalizing observation matrix by max value...")
        maxProb = numpy.amax(self.B_map)
        if inLogDomain:
            self.B_map -= maxProb
        else:
            self.B_map /= maxProb
        
    
    def _pdf(self,x,mean,covar):
        '''
        Deriving classes should implement this method. This is the specific
        Probability Distribution Function that will be used in each
        mixture component.
        '''        
        raise NotImplementedError("PDF function must be implemented")
    
    def _pdfAllFeatures(self,features,j):
        '''
        Deriving classes should implement this method.
        get the pdf of a series of features for models_makam j
        
        '''  
        raise NotImplementedError("PDF function must be implemented")
    
def _normalize(arr):
        '''
        Helper method to normalize probabilities, so that
        they all sum to '1'
        '''
        summ = numpy.sum(arr)
        for i in range(len(arr)):
            arr[i] = (arr[i]/summ)
        return arr
    
def logsumexp(arr, axis=0):
    """Computes the sum of arr assuming arr is in the log domain.
    
    TAKEN FROM sklearn/utils/extmath.py
    
    Returns log(sum(exp(arr))) while minimizing the possibility of
    over/underflow.
    
    Examples
    --------

    >>> import numpy as np
    >>> from sklearn.utils.extmath import logsumexp
    >>> a = np.arange(10)
    >>> np.log(np.sum(np.exp(a)))
    9.4586297444267107
    >>> logsumexp(a)
    9.4586297444267107
    """
    import sys
    MINIMAL_PROB = sys.float_info.min
    
    arr = np.rollaxis(arr, axis)
    # Use the max to normalize, as with the log this is what accumulates
    # the less errors
    vmax = arr.max(axis=0)
    old_settings = np.seterr( under='raise')
    try:
        a = np.exp(arr - vmax)
    except FloatingPointError:
        old_settings = np.seterr( under='ignore')
        a = np.exp(arr - vmax)
        a[a==0] = MINIMAL_PROB
    b = np.sum(a, axis=0)
    out = np.log(b)
    out += vmax
    
    old_settings = np.seterr( under='raise')
    return out

def cutOffHistogram( matrix_, cutOffIndex):
        '''
        assigns values in matrix_ below a threshold to be equal to MIN_PROB
        '''
        
        lenObs = matrix_.shape[1]
        for j in range(lenObs):
            # n-counts, edges - similarity values
#             counts, edges = numpy.histogram( numpy.e**(matrix_[:,j]) , bins = 5000) 
            counts, edges = numpy.histogram(matrix_[:,j],  bins = 100)
            #% cut after first cuttOffIndex peaks
            cutOffVal = edges[-cutOffIndex]
            cutOffVal = edges[cutOffIndex]
            
#             indices = numpy.where(numpy.e**(matrix_[:,j]) < cutOffVal)
            indices = numpy.where(matrix_[:,j] < cutOffVal)

            matrix_[indices, j] = MINIMAL_PROB
     
    
if __name__=='__main__':
    obsMatrixURI = '/Users/joro/Downloads/obsMatrix'
    obsMatrix = numpy.loadtxt(obsMatrixURI)
    cutOffHistogram(obsMatrix, cutOffIndex=2)
    print(obsMatrix)
    