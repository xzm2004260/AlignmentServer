# -*- coding: utf-8 -*-

'''
Created on May 23, 2017

@author: joro
'''

import os
import sys
import numpy as np

import contextlib
import wave
import re

from src.utilsLyrics.Utilz import loadTextFile
from src.align.SectionLink import _SectionLinkBase
from src.align.Lyrics import Lyrics
from src.for_english.CMUWord import CMUWord
from .ParametersAlgo import ParametersAlgo 
import mir_eval
import logging
from src.utilsLyrics.UtilsLyricsParsing import strip_line, load_section_annotations,\
    load_delimited

if ParametersAlgo.FOR_JINGJU:    
    from src.for_jingju.lyricsParser import createSyllable
    from src.for_jingju.LyricsMandarin import LyricsMandarin
    import pinyin as pinYin
    #from cjklib.characterlookup import CharacterLookup

non_pinyin = ['\uff08', '.']

TOLERANCE_END_SECTION = 0.3 # when with_section_annotations: tolerance overlapping section links (in seconds)

class StructuralSection():
    '''
    verse, chorus etc.
    '''
    def __init__(self, lyrics):
        self.lyrics = lyrics
        
class _RecordingBase():

    def __init__(self, mbRecordingID, audioFileURI, score):
        '''
        Constructor
        '''
        
        self.mbRecordingID = mbRecordingID
        
        self.recordingNoExtURI = os.path.splitext(audioFileURI)[0]  
        
        self.duration = get_duration_audio(self.recordingNoExtURI + '.wav')

        
        path, fileName = os.path.split(audioFileURI)
        path, self.which_fold = os.path.split(path) # which Fold
        
        self.score = score
        
        self.sectionLinks = []
        
    
    
    def _loadsectionTimeStampsLinks(self, sectionAnnosDict):
        raise NotImplementedError('_loadsectionTimeStamps links not impl')



class GenericRecording(_RecordingBase):
    '''
    input is lyrics as text file  
    '''
    def __init__(self, audioFileURI):
        _RecordingBase.__init__(self, 'dummy_recid', audioFileURI, 'dummy_score')            
        self.with_section_anno = None


    def load_lyrics(self, lyrics_URI, with_section_anno=0, language = 'English'):
        '''
        load the lyrics and create section Links
        
        Parameters:
        ----------- 
        lyrics_URI: - text file with the lyrics
        
        with_section_anno:
            if with annotations, each lyrics line has to be prepended by a timestamp 
            
        '''
        self.with_section_anno = with_section_anno
                
        if not os.path.isfile(lyrics_URI):
            sys.exit("no file {}".format(lyrics_URI))
        
        if with_section_anno == 1: # a section is a paragraph of lines
            start_times, section_lyrics = load_section_annotations(lyrics_URI)
            end_times = self.derive_end_times_sections(start_times) 
            lyrics_arr = []
            for lyrics_str in section_lyrics:
                lines = lyrics_str.split('\n')
                lyrics = lines_to_lyrics(language, lines)
                lyrics_arr.append(lyrics)

            
        elif with_section_anno == 2: # each line is a section. 
            start_times, lines = load_delimited(lyrics_URI, [float, str], delimiter='\t')
            end_times = self.derive_end_times_sections(start_times) 
            lyrics_arr = []
            for line in lines: # separate lyric object for each line
                lyrics, token_Objects_list = line_to_lyrics(language, line)
                lyrics_arr.append(lyrics)
                
        elif with_section_anno == 0: # the whole recording counts as the only section 
            lines = load_delimited(lyrics_URI, [str], delimiter='\t')
            start_times = [float(0)]; end_times = [float(self.duration)] # only one section anno

            lyrics = lines_to_lyrics(language, lines)
            lyrics_arr = [lyrics]  
        else: 
            sys.exit('section annotations could be only 0, 1 or 2')    
        
        self.create_section_links( start_times, end_times, lyrics_arr)
    
    
    def create_section_links(self, start_times, end_times, lyrics_arr):
        '''
        create objects of type Section Links from unstructured arrays of information
        '''
        for start_time, end_time, lyrics in zip(start_times, end_times, lyrics_arr):
            curr_sectionLink = _SectionLinkBase(self.recordingNoExtURI, start_time, end_time)
            structuralSection = StructuralSection(lyrics)
            curr_sectionLink.section = structuralSection
            self.sectionLinks.append(curr_sectionLink)    
            
    def derive_end_times_sections(self, start_times):
        '''
        get timestamps of ends of section links by copying start times and slightly extending them
        '''
        start_times = np.array(start_times)
        if start_times[-1] >= self.duration:
            sys.exit(' timestamp of last line {} is bigger than recording duration {}'.format(start_times[-1], self.duration ))
        
        end_times = start_times[1:-1] + TOLERANCE_END_SECTION # give some overlapp as tolerance to last word in sentence
        last_start_time = start_times[-1] 
        if last_start_time  + TOLERANCE_END_SECTION  >= self.duration: 
           butlast_end_time = last_start_time
        else:
           butlast_end_time = last_start_time  + TOLERANCE_END_SECTION 
        
        end_times = np.append( end_times, butlast_end_time)   
        end_times = np.append(end_times, self.duration)
        return end_times
    
    
    def print_words_of_lyrics(self):
        '''
        for each section print words
        '''
        for sectionLink in self.sectionLinks:
            print('section:\n')
            if hasattr(sectionLink, 'non_vocal_intervals'):
                print('non_vocal intervals: ' + str(sectionLink.non_vocal_intervals))
            
            sectionLink.section.lyrics.printWords()
#             sectionLink.section.lyrics.printPhonemeNetwork()
        
    def _loadsectionTimeStampsLinks(self, sectionAnnosDict):  
        '''
        @deprecated
        read begin and end ts of section (e.g. section link)
        ''' 
        
        ### sanity checks 
        if not os.path.isfile(sectionAnnosDict):
                sys.exit("no file {}".format(sectionAnnosDict))
         
        ext = os.path.splitext(os.path.basename(sectionAnnosDict))[1] 
        if ext != '.txt' and ext !='.tsv':
            sys.exit('Not supported extension for file {}'.format(sectionAnnosDict))
        
        lines = loadTextFile(sectionAnnosDict)
        
        if len(lines) != 1: # implemeted for one section only
            sys.exit('There are more than one ({}) sections'.format(len(lines))) 
        
        tokens =  lines[0].split() # get start and end ts
     
        section_link = _SectionLinkBase(self.recordingNoExtURI, float(tokens[0]), float(tokens[1]))
        self.sectionLinks.append(section_link)
    
    

    def vocal_intervals_to_section_links(self, vocal_intervals_URI):
        '''
        distribute the non vocal intervals for the whole recording into its sections
        '''
        _, non_vocal_intervals = self._load_vocal_intervals(vocal_intervals_URI)
        for section_link in self.sectionLinks:
            extracted_non_vocal_intervals = extract_non_vocal_in_interval(non_vocal_intervals, section_link.beginTs, section_link.endTs)
            reduced_time_shift_intervals = extracted_non_vocal_intervals - section_link.beginTs # should start from 0 for the audio of one section link
            section_link.non_vocal_intervals = reduced_time_shift_intervals
            
        
    def _load_vocal_intervals(self, vocal_intervals_URI):
            '''
            load intervals with singing voice fro URI, 
            computes the inverse - intervals with no voice
            
            Parameters
            vocal_intervals_URI: 
                txt file with intervals of type: <start_ts>\t<end_ts> per line
            
            Returns
            ----------------- 
            numpy.array [[]]
            
            '''
            # non_vocal_probs = self.classify_vocal() # vocal-non-vocal automatically
    #         voiced_intervals = numpy.array([[1,2],[5,6]])
            
            non_vocal_intervals = np.array([])
            vocal_intervals   = np.array([])
            
            if vocal_intervals_URI  is not None:
                vocal_intervals = mir_eval.io.load_intervals(vocal_intervals_URI)
                
                voiced_boundaries = mir_eval.util.intervals_to_boundaries(vocal_intervals) # they are even number
                
                if voiced_boundaries[0] <= 0: # no non-vocal interval in the beginning
                    voiced_boundaries = voiced_boundaries[1:]
                else: # non-vocal interval from 0 to voiced_boundaries[0]
                    voiced_boundaries = np.insert(voiced_boundaries, 0, 0) 
                
                if voiced_boundaries[-1] >= self.duration: # no non-vocal interval at the end
                    voiced_boundaries = voiced_boundaries[:-1]
                else: # non-vocal interval from  voiced_boundaries[-1] to the end
                    voiced_boundaries = np.append(voiced_boundaries, self.duration)
                
                if len(voiced_boundaries) != 0: 
                    all_intervals = mir_eval.util.boundaries_to_intervals(voiced_boundaries)
                    non_vocal_intervals = all_intervals[::2,:]
            
            return vocal_intervals, non_vocal_intervals


def line_to_tokens(line, token_Objects_list,  language):
    '''
    Parameters: 
    ----------------
    token object list: [str]
        list of lyrics tokens (usually words)
    
    line: str
        tokens as a string
    language:
        if Mandarin, apply a bit different logic because Mandarin characters are split in a differernt way.
    
    Returns
    ---------------
    token object list: [str]
        same list with appended tokens from current line
    
    '''
    line = line.strip()
    tokens = re.split(';|:|\*|-|\s', line)
    for token in tokens: # each  token (word or syllable) is separated by whitespaces
        if language == 'English':
            token_Objects_list.append(CMUWord(text=token))
        elif language == 'Mandarin':
            token_Objects_list = lineTxt_to_syllableList(token, token_Objects_list)
    word_silent = CMUWord(text='')
    word_silent.set_last_in_sentence(True)
    token_Objects_list.append(word_silent) # insert non-vocal token at the end of line
 
    return token_Objects_list

def tokens_to_lyrics_object(token_list, language = 'English'):
    '''
    create a lyrics object consisting of syllables from lines of tokens
    
    Parameters
    -----------
    
    tokens:
        list of lyrics tokens
    '''
    

    
    #### expand to phonemes
    if language == 'English':
        lyrics = Lyrics(token_list) 
    elif language == 'Mandarin': 
        lyrics = LyricsMandarin( token_list, 'dummy_banshi' )
    
    return lyrics

def lineTxt_to_syllableList(lineTxt, token_Objects_list):
    '''
    parse Mandarin characters. convert to a list of syllable objects
    
    Parameters
    ---------------------
    token_Objects_list: []
        list of to-this-point character objects
    lineTxt: str
        all characters of one text paragraph (line) together. characters have no white-space delimiters,
    '''
    pinyin = mandarinToPinyin(lineTxt)
    pinyin_syllables = pinyin.split()
    for pinyin_syllable in pinyin_syllables:
        if pinyin_syllable in non_pinyin: continue
        token_Objects_list = createSyllable(token_Objects_list, pinyin_syllable) # extend the list of syllables with the new syllable
    token_Objects_list = createSyllable(token_Objects_list, '') # add silence syllable at end of line
    
    return token_Objects_list

def mandarinToPinyin(mandarinChar):

# some cahracters of lyrics of pop songs are not in CJK! 
#         cjk = CharacterLookup('C')
#         textPinYinList = cjk.getReadingForCharacter(mandarinChar, 'Pinyin', toneMarkType='none')
#         
#         if len(textPinYinList) > 1:
#             print "converted syllable {} has {} parts".format(textPinYinList, len(textPinYinList)) 
#         pinyin = textPinYinList[0] # take only first variant of pinyin interpretations

        pinyin = pinYin.get(mandarinChar, format="strip", delimiter=" ")
       
        
        return pinyin
    
def get_duration_audio(filename):
    '''
    get duration in seconds of .wav file 
    
    copied from https://github.com/georgid/AlignmentEvaluation/blob/master/align_eval/Utilz.py
    to reduce project dependency
    '''
    if not os.path.isfile(filename):
        logging.warning(filename + ' does not exist. Returning default duration of 3 minutes')
        return 180
    
    with contextlib.closing(wave.open(filename,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration

def extract_non_vocal_in_interval(intervals, start_time, end_time):
    '''
    intersect non_vocal intervals: extract the subset of non_vocal intervals in the interval between 
    start_time and end_time.  cut interval boundaries 
    '''
    if len(intervals) == 0:
        return np.array([])
    if end_time <= np.min(intervals) or start_time >= np.max(intervals):
        return np.array([])

    est_labels = len(intervals) * ['a']
    intervals, est_labels = mir_eval.util.adjust_intervals(
        intervals, est_labels, start_time, end_time)
        
    if est_labels[0] == '__T_MIN':
        intervals = intervals[1:]
    if est_labels[-1] == '__T_MAX':
        intervals = intervals[:-1]
    return intervals

def line_to_lyrics(language, line):
    '''
    helper
    '''
    token_Objects_list = [CMUWord(text='')] # insert silence at beginning of line
    token_Objects_list = line_to_tokens(line, token_Objects_list, language) # it inserts silence also at the end
    lyrics = tokens_to_lyrics_object(token_Objects_list, language)
    lyrics.set_lines([strip_line(line)])
    return lyrics, token_Objects_list

def lines_to_lyrics( language, lines):
    '''
    helper for processing all lines from text file
    '''
    token_Objects_list = []
    lines_stripped = [] 
    for line in lines:
        if type(line) == int: continue # skip empty lines which we marked earlier by a flag -1
        lines_stripped.append(strip_line(line))
        token_Objects_list = line_to_tokens(line, token_Objects_list, language)

    lyrics = tokens_to_lyrics_object(token_Objects_list, language)
    lyrics.set_lines(lines_stripped)
    return lyrics
