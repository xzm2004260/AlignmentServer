'''
Created on Sep 3, 2017

@author: Georgi
'''

import numpy


from src.hmm.continuous._HMM import _HMM

from src.hmm.continuous._ContinuousHMM import _ContinuousHMM

from src.align.ParametersAlgo import ParametersAlgo
import sys
import os

currentPath = os.path.dirname(__file__)
parentDir = os.path.join(currentPath , os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir )

jingjuPhraseDir = os.path.join(parentDir, 'jingjuSingingPhraseMatching/phoneticSimilarity/lyricsRecognizer')
if jingjuPhraseDir not in sys.path: sys.path.append(jingjuPhraseDir)

MODEL_PATH = os.path.join(parentDir, 'jingjuSingingPhraseMatching/phoneticSimilarity/cnnModels/qmLonUpf/laosheng/keras.cnn_mfccBands_2D_all_optim.h5')
# MODEL_PATH = os.path.join(parentDir, 'jingjuSingingPhraseMatching/phoneticSimilarity/cnnModels/danAll/keras.cnn_mfccBands_2D_all_optim.h5')


from general.phonemeMap import dic_pho_label
from ParallelLRHMM import ParallelLRHMM



# from _ContinuousHMM import _ContinuousHMM
class CNNHMM(_HMM):
    '''
    A CNN HMM - This is a representation of a continuous HMM,
    containing Convolutional Neural Network in each hidden state.
    
    It is essentially a wrapper around the model loaded from 
    https://github.com/ronggong/jingjuSingingPhraseMatching/tree/master/phoneticSimilarity/cnnModels
    
    For more information, refer to _ContinuousHMM.
    '''


        
    def __init__(self, statesNetwork,  transMatrices):
        '''
        See base class constructor for more information
        '''
        _HMM.__init__(self, statesNetwork, transMatrices)
        
        
        if ParametersAlgo.FOR_JINGJU: 
            self.phn_to_stateidx = 1
        else: # other languages
            sys.exit('implmented only for Mandarin')
        self._load_model()
            
    def _load_model(self):
        '''
        load keras model here  
        '''
        self.model = ParallelLRHMM.kerasModel(MODEL_PATH)
    
    def _mapB(self, features):
        '''
        extend base method. first load all output with given MLP
        takes time, so better do it in advance to _pdfAllFeatures(), becasue _ContinuousHMM._mapB calls _pdfAllFeatures()
        '''
        if not ParametersAlgo.USE_PERSISTENT_PPGs or not os.path.exists(self.PATH_BMAP):
#             self.mlp_posteriograms = self.recogn_with_MLP( features) ## posteriograms, no log applied
            observations_concat = [features, features, features, features, features, features]

            ##-- call keras to calculate the observation from the features
            self.cnn_posteriograms = self.model.predict_proba(observations_concat, batch_size=128,verbose=0)
        _ContinuousHMM._mapB(self, features)
        
        
    def _pdfAllFeatures(self,features,j):
        '''
        get the log likelohood of a series of features for the model that corresponds to state j.
        
        called from _Continuous._mapB()
        
        -----------------------
        Returns 
        log likelihoods p(Y_1:T | j)
        '''
#         old_settings = numpy.seterr(under='warn')
        
        #### get index of the model of the phoneme that corresponds to the given state j from the state sequence
        curr_phoneme_ID = self.statesNetwork[j].phoneme.ID
        if curr_phoneme_ID not in dic_pho_label:
                print 'phoneme {} not in dict'.format(curr_phoneme_ID)
                phoneme_idx = 0
        else:
            phoneme_idx = dic_pho_label[curr_phoneme_ID] # index of letter
            

        probs_phoneme = self.cnn_posteriograms[:,phoneme_idx]
        logprob = numpy.log(probs_phoneme)
        return logprob  
    
