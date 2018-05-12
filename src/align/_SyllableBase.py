'''
Created on Mar 5, 2015

@author: joro
'''
import sys

from src.align.ParametersAlgo import ParametersAlgo

SIL_TEXT = 'sp' # text of silent phoneme
if not ParametersAlgo.FOR_JINGJU and not ParametersAlgo.FOR_MAKAM: # ENGlish, use CMU phoneme set
    SIL_TEXT = 'pau' 

if ParametersAlgo.OBS_MODEL == 'CNN' and ParametersAlgo.FOR_JINGJU: # using x-sampa phoneme set
    SIL_TEXT = ''

    
class _SyllableBase():
        ''' syllables class done because in symbolic file lyrics are represented as syllables
        BUT not meant to be used alone, instead Syllable is a part of a Word class
        '''
        def __init__(self, text='', noteNum=-1):
            # strip commas: 
            
            text = text.replace(',','')
            self.text = text
            
#             corresponding note num
            self.noteNum = int(noteNum)
            self.phonemes = []
            self.durationInMinUnit = None
            self.durationInNumFrames =  None

            self.hasShortPauseAtEnd = False
            
        def setHasShortPauseAtEnd (self, hasShortPauseAtEnd): 
            '''
            set if this is last syllable in word
            '''
            self.hasShortPauseAtEnd = hasShortPauseAtEnd
        
        def setDurationInMinUnit(self, duration):
            self.durationInMinUnit = duration
            
        def getDurationInMinUnit(self):
            return self.durationInMinUnit
       
        def setDurationInNumFrames(self, durInNumFrames):
            self.durationInNumFrames =  durInNumFrames
        
        def expandToPhonemes(self):
            '''
            make sure text has no whitespaces
            '''
            
            raise NotImplementedError("in class SyllableBase. expoandToPhoenemes not implemented")
           
            
        def getPhonemes(self):
            return self.phonemes
        
        def getNumPhonemes(self):
            if self.phonemes == []:
                self.expandToPhonemes()
            return len(self.phonemes)
        
        def getPositionVowel(self):
            '''
            which is the vowel phoneme. 
            check vowels in lookup table
            NOTE: assume only one vowel in syllable. this is true if no diphtongs in language 
            '''
            if self.getNumPhonemes() == 0:
                return -1
            for i, phoneme in enumerate(self.phonemes):
                if phoneme.isVowel():
                    return i
            return -1
        
        def calcPhonemeDurations(self):
            '''
            consonant handling policy
            all consonant durations set to 1 unit, the rest for the vowel.
           '''
            raise NotImplementedError("in class SyllableBase. expoandToPhonemes not implemented")
        
        
        def setPhonemeDurations(self, listDurations):
            if self.phonemes is []:
                self.expandToPhonemes()
            
            if self.getNumPhonemes() == 0:
                sys.exit("syllable with no phonemes!")
                return
            
            if len(self.phonemes) != len(listDurations):
                sys.exit("syllable {} has {} phonemes but given durations list has {}".format(self.text, len(self.phonemes), len(listDurations)))
                for currPhoneme, currDuration in zip(self.phonemes, listDurations):
                        currPhoneme.durationInNumFrames = currDuration
                
        def __str__(self):
                syllalbeTest = self.text.encode('utf-8','replace')
                return syllalbeTest + " durationInMinUnit: " + str(self.durationInMinUnit) + "\n" 
            
            
# begin index does not update, because no change in aranagme. 




