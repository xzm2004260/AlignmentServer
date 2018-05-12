# -*- coding: utf-8 -*-
'''
Created on May 24, 2017

@author: joro

# Info for 'cmudict.0.6d.syll':
#
# The following file contains the CMU Pronouncing Dictionary version 0.6 augmented with syllable boundaries (syllabified CMU).
# The boundaries were generated automatically using a structured SVM approach, which was shown to correctly syllabify over 98% words in the CELEX dictionary.
# If you use this data in your work, please cite the following paper:
#
# Susan Bartlett, Grzegorz Kondrak and Colin Cherry.
# On the Syllabification of Phonemes.
# NAACL-HLT 2009.

'''
import sys
import string

import Levenshtein

import logging
import inflect
inflect_engine = inflect.engine()


from src.align.Word import Word
from src.align._SyllableBase import _SyllableBase, SIL_TEXT
from src.align.ParametersAlgo import ParametersAlgo
from src.align._PhonemeBase import PhonemeBase
from src.align.Phonetizer import Phonetizer


# LIST_SUSP_CHARS = [u"≈", u"~", u"@", u"[", u"]", u'.....'] 
# LIST_SUSP_CHARS = [u"≈", u"@", u"[", u"]", u'.....'] 
LIST_SUSP_CHARS = ["≈", "@", "[", "]"]     # list of suspicious chars
class CMUWord(Word):
    '''
    word based on CMU transcription rules given here http://www.speech.cs.cmu.edu/cgi-bin/cmudict
    '''


    input_func_name = None # prompt input . in test cases different
    
    
    def expandToPhonemes(self):
        '''
        phonetization using dict
        '''
        
        
        self.syllables =  []
        
        if self.text == '': # if the word has empty text, expands to one-syllable of silent phoneme 
            currSyllable = _SyllableBase()
            phonemeSp = PhonemeBase(SIL_TEXT)
            currSyllable.phonemes.append(phonemeSp)
            self.syllables.append(currSyllable)
            return
        
          
        phonemes_grouped = self._word_to_syllables() # complex words could consist of more than one simpler words (e.g. two-digit numbers like  are such)

        ##### parse all into list of syllables
        for curr_syll_phonemes in phonemes_grouped: # create each syllable
            
            currSyllable = _SyllableBase()
            curr_phonemes = curr_syll_phonemes.split(' ')
            for phonemeID in curr_phonemes: # for each phoneme in syllable
                    currSyllable.phonemes.append(PhonemeBase(phonemeID))
            self.syllables.append(currSyllable)
                 
                
            
        if ParametersAlgo.WITH_SHORT_PAUSES: # add a short pause at the end
            self.phonemes.append(PhonemeBase(SIL_TEXT))

    def _word_to_syllables(self):
        '''
        expand text of word into phonemes 
        returns phonemes grouped into syllables
        '''
        
        
        if hasNumbers(self.text): # each number part is treated as a separate word 
            self.text = number_to_words(self.text)
            number_words = self.text.split()
            phonemes_grouped_all = []     
            for word in number_words: 
                phonemes_grouped = _trans(word, Phonetizer.phoneticDict)
                phonemes_grouped_all.extend(phonemes_grouped)
        else:
            phonemes_grouped_all = _trans(self.text, Phonetizer.phoneticDict)
#         phonetized_syllables = phonetized_syllables[0] # list of word: it has only one word
        return phonemes_grouped_all

    def normalize_ortography(self):
        ortography = self.text 
        if self.stop_on_suspicous_chars(self.input_func_name):
            print(('suspicios word is {}'.format(self.text)))
            sys.exit('Requested termination. Terminating...')
        
        self.text = replace_special_chars(self.text)
        
        def ending(word_ortho):
            return '\'' if word_ortho.endswith('\'') else ''  # allow words ending in ', e.g. feelin'
            
        if ending(self.text) == "'":
            self.text = self.text.strip(string.punctuation) + 'g'
        else:
            self.text = self.text.strip(string.punctuation)
        
        is_only_punctuation = False
        if ortography != '' and self.text == '':
            is_only_punctuation = True
        return is_only_punctuation
    
    def stop_on_suspicous_chars(self, func_name):
        '''
        returns true if a word contains unacceptable lyrics 
        '''
    
        for susp_char in LIST_SUSP_CHARS:
            if susp_char in self.text:
                answer = func_name()
                return answer != 'y' # if user not sure, stop

def check_underscores(word):
    '''
    TODO: unfinished
    '''
    if word.contains('_'):
        sys.exit('The word {} contains underscore(_). It is ambiguous if this connects two separate words or is a marker within one word. \
        Please press enter to split word'.format(word))



 
def _trans(word_ortho, lex):
    '''
    convert orthographic word into a phoneme sequence
    code modified from Merlijn
    
    Parameters
    ----------------------
    ortho: str
        word as written in lyrics file
    lex: dict()
        dictionary
    
    Return
    ----------------------
    words_phone: list of words
    
    '''
    

    # lexicon lookup
    wordInLex, phonemes = word_to_sylls(word_ortho, lex, variant=0)  # use first variant by default
    
    if not wordInLex: # workaround:  replacing a  word not in dict with the phonemes of the one with closest ortography
        word_replaced = find_word_replacement(word_ortho, lex)
        logging.debug('word {} not in dict. replacing with {}'.format(word_ortho, word_replaced))
        wordInLex, phonemes = word_to_sylls(word_replaced, lex, variant=0)
    

#     phone = ' '.join(words_phone) # put space between words
    return phonemes

def replace_special_chars(ortho_word):
    # lower case orthography
    ortho_word = ortho_word.lower()

#     ortho_word = ortho_word.replace('_',"'")
    ortho_word = ortho_word.replace("’","'")
    ortho_word = ortho_word.replace("^","i") # convention for dirty words in some rap songs
    for char in LIST_SUSP_CHARS:
        ortho_word = ortho_word.replace(char,"")
        
    return ortho_word

def word_to_sylls(word_ortho, lex, variant=0):
    '''
    normalize punctuation word
    '''
    if word_ortho not in lex or len(lex[word_ortho]) == 0:
        return False, word_ortho
    else:
        sylls_stresses = lex[word_ortho][variant]
        sylls = [syll for syll, stress in sylls_stresses]
        return True, sylls  

def find_word_replacement(word_ortho, lex):
    '''
    find the word with most similar ortography. 
    TODO: use sorted dict, to reduce the time complexity of exhaustive loop
    TODO: better is to find the one with most similar sound 
    '''
    word_replaced = ''
    min_dist = 1000
    
    for word_lex in list(lex.keys()):
        try:
            word_ortho_str = str(word_ortho)
        except:
            word_ortho_str = str(word_ortho, encoding='utf8')
        dist_ = Levenshtein.distance(word_lex, word_ortho_str)
        if dist_ < min_dist:
            min_dist = dist_
            word_replaced = word_lex
        
        if dist_ <= 1: # workaround, 2-symbol difference considered ok
            word_replaced = word_lex
            break
    return word_replaced
    
def is_arpabet_vowel(phn):
    return phn in ['aa', 'ae', 'ah', 'ao', 'aw', 'ay', 'ax', 'eh', 'er', 'ey', 'ih', 'iy', 'ow', 'oy', 'uh', 'uw']


def number_to_words(number):
    '''
    convert number in digits to a word, 
    example: 21 -> twentyone
    '''
    try:
        num_in_words = inflect_engine.number_to_words(number)
    except:
        sys.exit('The word {} contains digits, but is not a number'.format(number))
    num_in_words = num_in_words.replace('-',' ')
    return num_in_words

def hasNumbers(inputString):
    '''
    a string contains numbers?
    '''
    return any(char.isdigit() for char in inputString)