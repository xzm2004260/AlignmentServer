'''
Created on Dec 28, 2015

@author: joro
'''
import sys
import os
import numpy as np

from .ParametersAlgo import ParametersAlgo
from src.align._LyricsWithModelsBase import _LyricsWithModelsBase
from src.align.FeatureExtractor import MODEL_PATH
import logging
import time
from src.align.separate import separate
import tempfile

class _SectionLinkBase():

    
    def __init__(self, URIWholeRecording_noExtension, beginTs, endTs):
        '''
        Constructor
        '''
        basename = os.path.basename(URIWholeRecording_noExtension)

        self.beginTs = beginTs
        self.endTs = endTs
        audioTmpDir = tempfile.mkdtemp()
        self.URIRecordingChunk = os.path.join(audioTmpDir, basename + "_" + "{}".format(self.beginTs) + '_' + "{}".format(self.endTs))
#         self.URIRecordingChunk = URIWholeRecording_noExtension

# WITHOUT TEMP DIR: 
#         dirname_ = os.path.dirname(URIWholeRecording_noExtension)
#         self.URIRecordingChunk = os.path.join(dirname_, basename + "_" + "{}".format(beginTs) + '_' + "{}".format(endTs))

        
        
        # composition section. could be LyricsSection or ScoreSection
        self.section = None
        
        self.non_vocal_intervals = np.array([])
        
        
    def setSection(self, section):
        '''
        could be LyricsSection or ScoreSection
        '''
        self.section = section
        
      
    def setSelectedSections(self, sections):
        '''
        selected sections after alignment with lyrics refinement 
        '''
        self.selectedSections = sections
    
    def set_begin_end_indices(self, token_begin_idx, token_end_idx):
        '''
        the indices in the annotation TextGrid
        '''
        self.token_begin_idx = token_begin_idx
        self.token_end_idx = token_end_idx
    
    def createLyricsModels( self, featureVectors = None):
        '''
        test duration-explicit HMM with audio features from real recording and htk-loaded htkParserOrFold
        asserts it works. no results provided 
        '''
        
        if ParametersAlgo.FOR_JINGJU: # they are one-state GMM
                      
            if ParametersAlgo.OBS_MODEL == 'CNN':
                from src.align.LyricsWithModelsCNN import LyricsWithModelsCNN
                self.lyricsWithModels = LyricsWithModelsCNN(self.section.lyrics, None, ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)

            else: sys.exit('Working with mandarin... only CNN model implemented for Mandarin')
                
        else:
            self.lyricsWithModels = _LyricsWithModelsBase(self.section.lyrics, None, ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
    
        if ParametersAlgo.WITH_DURATIONS:
            if self.lyricsWithModels.lyrics.getTotalDuration() == 0:
                sys.exit("total duration of segment {} = 0".format(self.URIRecordingChunk))
                return None, None, None
            if featureVectors is None:
                sys.exit('featureVectors is not given. it is needed to get duration')
            # needed only with duration
            self.lyricsWithModels.duration2numFrameDuration(featureVectors, self.URIRecordingChunk)
        self.lyricsWithModels._phonemes2stateNetwork()

#         self.lyricsWithModels.printPhonemeNetwork()

    def get_audio_segment(self, audio, sample_rate):
        '''
        gets the audio_segment segment for this section fromt the audio_segment for the complete recording
        '''
        begin_sample = int(self.beginTs * sample_rate)
        end_sample = int(self.endTs * sample_rate)
        audio_segment = audio[begin_sample : end_sample]
        return audio_segment
    
    def separate_vocal(self, audio, sample_rate):
        '''
        Parameters
        --------------------
        audio: array [] 
            the audio for the complete recording
        sample_rate: int
            read sampling rate
        '''
        # segregate vocal part from whole recording
        model_URI = os.path.join(MODEL_PATH, 'krast.dad')



        logging.info("doing source separation for recording: {} ...".format(self.URIRecordingChunk))
        if sample_rate != 44100: # source separation is hard coded to work with 44100.
            msg = 'sample rate is not 44100. source separation is hard coded to work with 44100'
            raise RuntimeError(msg)
        time0 = time.time()
        
        audio_sep = separate(audio, model_URI, 0.3, 30, 25, 32, 513)

        time1 = time.time()
        logging.info(" source separation: {} seconds".format(time1 - time0))
        return audio_sep
    
    def loadSmallAudioFragmentOracle(self):
        raise NotImplementedError('loadSmallAudioFragmentOracle not implemeted')    
        
    
    def __repr__(self):
        return "Section from  {}  to {}".format( self.beginTs, self.endTs)
        
        

