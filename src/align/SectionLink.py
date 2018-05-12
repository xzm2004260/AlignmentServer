'''
Created on Dec 28, 2015

@author: joro
'''
import sys
import tempfile
import os
import numpy as np

from .ParametersAlgo import ParametersAlgo
from src.align._LyricsWithModelsBase import _LyricsWithModelsBase
audioTmpDir = tempfile.mkdtemp()

class _SectionLinkBase():

    
    def __init__(self, URIWholeRecording_noExtension, beginTs, endTs):
        '''
        Constructor
        '''
        basename = os.path.basename(URIWholeRecording_noExtension)
        dirname_ = os.path.dirname(URIWholeRecording_noExtension)
#         self.URIRecordingChunk = os.path.join(audioTmpDir, basename + "_" + "{}".format(beginTs) + '_' + "{}".format(endTs))
        self.URIRecordingChunk = os.path.join(dirname_, basename + "_" + "{}".format(beginTs) + '_' + "{}".format(endTs))
        self.URIRecordingChunk = URIWholeRecording_noExtension
        
        self.beginTs = beginTs
        self.endTs = endTs
        
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

    
    
    def loadSmallAudioFragmentOracle(self):
        raise NotImplementedError('loadSmallAudioFragmentOracle not implemeted')    
        
    
    def __repr__(self):
        return "Section from  {}  to {}".format( self.beginTs, self.endTs)
        
        

class SectionLinkMakam(_SectionLinkBase):
    '''
    as output of SectionLink  has match to only melodicStrcuture, so it is ambiguous and needs matching
    '''
    

    def __init__(self, URIWholeRecording, melodicStructure, beginTs, endTs):
        '''
        Constructor
        '''
        _SectionLinkBase.__init__(self, URIWholeRecording, beginTs, endTs)
        self.melodicStructure = melodicStructure
  
        
        
        
        

        


          
              
        
        
class SectionAnnoMakam(SectionLinkMakam):
    '''
    sectionAnno has a link to exactSetion through tuple (melodicStructure, lyricsStucture)
    SO it can be matched unambigously to a particular ScoreSection
    '''
    
    def __init__(self, URIWholeRecording, melodicStructure, lyricStructure, beginTs, endTs):
        SectionLinkMakam.__init__(self, URIWholeRecording, melodicStructure, beginTs, endTs)
        self.lyricStructure = lyricStructure
        
    
    def matchToSection(self,  scoreSections):
        if self.lyricStructure == None:
           sys.exit('cannot match link to section. No lyricStructure defined')
        
        for scoreSection in scoreSections:
            if self.melodicStructure == scoreSection.melodicStructure and self.lyricStructure == scoreSection.lyricStructure:
                self.setSection(scoreSection)
                break  