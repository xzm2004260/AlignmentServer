'''
Created on May 20, 2016

@author: joro
'''
import os
import sys
import numpy

### include src folder
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)
    
from .ParametersAlgo import ParametersAlgo
        

class PhonemeBase(object):
    '''
    classdocs
    '''


    def __init__(self, phonemeID):
        self.ID = phonemeID;
        self.durationInMinUnit = None;
        self.durationInNumFrames = None;
        self.numFirstState = -1
        
        self.lastInSyll = False
        self.isModelType = None
    
    def setBeginTs(self, beginTs):
        '''
        begin ts from annotation
        '''
        self.beginTs = beginTs
    
    def setEndTs(self, endTs):
        '''
        begin ts from annotation
        '''
        self.endTs = endTs
            
    def setNumFirstState(self, numFirstState):
            self.numFirstState = numFirstState
        

    def setDurationInNumFrames(self, dur):
        self.durationInNumFrames =    dur; 
    
 
    
    def setModel(self, model):
        '''
        could be sciKitGMM or htkConverter object 
        '''
        
            
        self.model =  model
        if ParametersAlgo.OBS_MODEL == 'MLP' or ParametersAlgo.OBS_MODEL == 'MLP_fuzzy':
            self.isModelType = 'theano'
             
        elif ParametersAlgo.OBS_MODEL == 'GMM' and ParametersAlgo.FOR_MAKAM: # isinstance(model, htkparser.htk_models.Hmm):
            self.isModelType = 'htk'
        elif isinstance(model, SciKitGMM):
            self.isModelType = 'scikitGMM' 
        else:
            sys.exit("model for phoneme {} is neither htk nor sciKitGMM ".format(self.ID) )

        
        
    
    def getTransMatrix(self):
        '''
        read the trans matrix from models_makam. 
        3x3 or 1x1 matrix for emitting states only.
        as numpy array
        '''
        
        try: self.model
        except AttributeError:
                sys.exit("  phoneme {} has no models_makam assigned ".format(self.ID) )
        
        
        if not self.isModelType == 'htk':
                    sys.exit("trans matrix defined only for htk models_makam" )

        vector_ = self.model.tmat.vector
        currTransMat = numpy.reshape(vector_ ,(len(vector_ )**0.5, len(vector_ )**0.5))
    
        return currTransMat  
    
    
    def getNumStates(self):
        '''
        return the number of states that are associated with this phoneme
        based on assigned htk models
        '''
        

            
        if self.isModelType == 'htk':
            try: self.model
            except AttributeError:
                sys.exit("cannot get numstates. phoneme {} has no htk or gmm models_makam assigned ".format(self.ID))
            if ParametersAlgo.ONLY_MIDDLE_STATE:
                lenStates = 1
            
            else:
                if (self.model.tmat.numStates - 2) != len(self.model.states):
                    sys.exit('num states in matrix differs from num states in htk ')
                lenStates = len(self.model.states)
        
        else:
            lenStates = 1
        
        return lenStates
    
        
    def isLastInSyll(self):
        return self.lastInSyll
    
    def setIsLastInSyll(self, lastInSyll):
        self.lastInSyll = lastInSyll
    
    def __str__(self):
        string_phoneme = self.ID
        if self.lastInSyll:
            string_phoneme+= " :last in syllable " 
        return string_phoneme
     
    def __repr__(self):
        return self.ID
    
    
    def isVowel(self):
        raise NotImplementedError("Phoneme.isVowe not implemented")

class SciKitGMM(object):
    '''
    convenienve class wrapper for scikit-learns gmm model
    '''


    def __init__(self, gmm, modelName):
        '''
        Constructor
        '''
        self.gmm = gmm
        self.modelName = modelName 