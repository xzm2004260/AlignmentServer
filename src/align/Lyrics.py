'''
Created on Oct 27, 2014

@author: joro
'''
import sys

class Lyrics(object):
    '''
    Lyrics data structures
    represents lyrics for one structural section as list of words
    appends sil at start and end of sequence

    '''


    def __init__(self, listWords):
        '''
        Word[]
        '''
        self.listWords = listWords
        '''
        Phoneme [] : list of phonemes
        '''
        self.phonemesNetwork =  []
        
        self._graphemes2Phonemes()
        
    
    def _graphemes2Phonemes(self):
        ''' convert list of words (Word []) to 
        @return: self.phonemesNetwork: 
        '''
      
        ### loop through all words to combine phonemes network
        cleaned_word_list = []
        for word_ in self.listWords:
            is_only_punctuation = word_.normalize_ortography()
            if not is_only_punctuation: # do not consider as words only-punctuation tokens 
                cleaned_word_list.append(word_)
                
        self.listWords = cleaned_word_list
        for word_ in self.listWords:
            word_.expandToPhonemes()
            for syllable_ in word_.syllables:
                phonemesInSyll = syllable_.getPhonemes()
                phonemesInSyll[-1].setIsLastInSyll(True)
                
                self.phonemesNetwork.extend(phonemesInSyll )
            
#             word_.setNumFirstPhoneme(currNumPhoneme)
            # update index
#             currNumPhoneme += word_.getNumPhonemes()
        

    
    def calcPhonemeDurs(self):
        '''
        for each word calculate the phoneme durations for its constituent syllables
        '''
        for word_ in self.listWords:
            for syllable in word_.syllables:
                syllable.calcPhonemeDurations()
    
    def printWords(self):
        for word_ in self.listWords:
            print("\t",  word_ , ":") 
            for syllable_ in word_.syllables:
                    print("\t\t : " , syllable_.text)
                    if word_.is_last_in_sentence():
                        print("\n end of sentence. \n")     
    
    def printSyllables(self):
        '''
        debug: print syllables 
        '''
        for word_ in self.listWords:
                for syllable_    in word_.syllables:
                    print(syllable_)
#                     for phoneme_ in syllable_.phonemes:
#                         print "\t phoneme: " , phoneme_
                    
                    
    def getTotalDuration(self):
        '''
        total durationInMinUnit of phonemes according to score. no pauses considered.
        '''
        totalDuration = 0.0    
        if len(self.listWords) == 0:
            sys.exit("no words in lyrics set. No total duration can be get")    
        for word_ in self.listWords:
            for syllable_ in word_.syllables:
                totalDuration +=  syllable_.durationInMinUnit
        return totalDuration
            
    
    def printPhonemeNetwork(self):
        '''
        debug: score-derived phoneme  durationInMinUnit 
        '''
               
        for i, phoneme in enumerate(self.phonemesNetwork):
            print("{}: {} {}".format(i, phoneme.__str__(), phoneme.durationInMinUnit))
#                         print "{}".format(phoneme.ID)
    def set_lines(self, lyrics_lines):
        '''
        lyric_lines are the raw lines as read from the txt file
        '''
        self.lyrics_lines = lyrics_lines
                 
    def __str__(self):
        lyricsStr = ''
        for word_ in self.listWords:
            lyricsStr += word_.__str__().decode('utf-8') # __str__ in python 3 returns bytes, decode returns it into str 
            lyricsStr += ' '
        a = lyricsStr.rstrip()
        return a 
    
    
    def getLenNoRests(self):
        lenWords = 0
        for word_ in self.listWords:
            if word_.syllables[0].text != 'REST':
                lenWords += 1
        return lenWords