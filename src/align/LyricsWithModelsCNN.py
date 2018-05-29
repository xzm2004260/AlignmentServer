'''
Created on May 7, 2016

@author: joro
'''
from _LyricsWithModelsBase import _LyricsWithModelsBase
from ParametersAlgo import ParametersAlgo

if ParametersAlgo.FOR_JINGJU:
    from general.phonemeMap import  dic_pho_map

class LyricsWithModelsCNN(_LyricsWithModelsBase):
    '''
    This class is done exclusively for Mandarin since CNN models are used only for Mandarin so far.
    '''

    
    def _linkToModels(self, htkParser):
        '''
        CNN models are not separate classes, but part of a network, so no linking is done.
        Instead it renames phonemes using a mapping to the actual CNN classes 
        
        add  Phoneme('sp') with exponential distrib at beginning and end if withPaddedSilence 
        '''
       
        
        _LyricsWithModelsBase._addPaddedSilencePhonemes(self)   
        
        ##### rename each phoneme to a model
        for phonemeFromTranscript in    self.lyrics.phonemesNetwork:
            pho_map = dic_pho_map[phonemeFromTranscript.ID]
            if pho_map == u'H':
                pho_map = u'y'
            elif pho_map == u'9':
                pho_map = u'S'
            elif pho_map == u'yn':
                pho_map = u'in'
            phonemeFromTranscript.ID = pho_map
                
    
    
    
    

          
        