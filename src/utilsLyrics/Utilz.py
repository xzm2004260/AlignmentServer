'''
Created on Mar 12, 2014

@author: joro
'''

import codecs
import numpy
import os
import sys

import difflib
import glob
import csv
import json
import math

from src.align.ParametersAlgo import ParametersAlgo

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
sys.path.append(parentDir)

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

    ##################################################################################

def loadDictFromTabFile(fileURI):
    
    dict_ = {}
    with open(fileURI) as file_object:
        for entry in file_object:
            (key, val) = entry.split()
            dict_[key] = val
    return dict_


def writeCsv(fileURI, list_, withListOfRows=1):
    '''
    TODO: move to utilsLyrics
    '''
    from csv import writer
    fout = open(fileURI, 'wb')
    w = writer(fout)
    print('writing to csv file {}...'.format(fileURI))
    for row in list_:
        if withListOfRows:
            w.writerow(row)
        else:
            tuple_note = [row.onsetTime, row.noteDuration]
            w.writerow(tuple_note)
    
    fout.close()

def findFileByExtensions(pathToComposition, listExtensions):
    '''
    @return: name (with no dir) of first found file 
    '''
    
#     listExtensions = ["sections.txt", "sections.tsv", "sections.json"]
    if not listExtensions:
        msg = "{} is empty".format(listExtensions)
        raise RuntimeError(msg)

    os.chdir(pathToComposition)

    sectionFiles = glob.glob("*." + listExtensions[0])
    if not sectionFiles:
        sectionFiles = glob.glob("*." + listExtensions[1])
        if not sectionFiles:
                sectionFiles = glob.glob("*." + listExtensions[2])
    return sectionFiles

def findFilesByExtension(pathToComposition, extension):
    '''
    with pattern name_name.wav
    '''
    sectionFiles = glob.glob(pathToComposition + "[a-z]*_*[a-z]." + extension)

    return sectionFiles

def matchSections(s1, s2, indicesS2):
    '''
    MAtch automatically the section names in s2 to these in s1. 
    @param indicesS2: for each lelement in s2 -> to which element in s1 corresponds: give it empty. 
    @return:  the inidices for s2 indicating the matched sections in s1 
    '''
  
    for (i,a) in enumerate(s1):
        s1[i]= s1[i].lower()
    for (i,a) in enumerate(s2):
        s2[i]= s2[i].lower()
     
    matcher = difflib.SequenceMatcher(None,s1,s2)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            print('The sections [%d:%d] of s1 and [%d:%d] of s2 are the same' % \
                (i1, i2, j1, j2))
            for c in range(i1,i2):
                indicesS2.append(c)

        elif tag == 'insert':
            print('Insert %s from [%d:%d] of s2 into s1 at %d' % \
                (s2[j1:j2], j1, j2, i1))
            indicesS2 = matchSections(s1,s2[j1:j2], indicesS2)

        # section not present in score
        elif tag == 'replace':
            print('{} replaced with {}. add -1 because not present in score'.format( s1[i1:i2], s2[j1:j2]))
            for c in range(j1,j2):
                indicesS2.append(-1) 
           
    return indicesS2
            
    
## TODO: callback function to load code. Put it in a different folder

def loadTextFile( pathToFile):
        '''
        helper method to load all lines from a text file
        @deprecated. replaced by  src.utilsLyrics.UtilsLyricsParsing.load_delimited 
        '''
        
        # U means cross-platform  end-line character
#         inputFileHandle = codecs.open(pathToFile, 'rU', 'utf-8', errors='ignore')
        inputFileHandle = codecs.open(pathToFile, 'rU', 'utf-8')

        
        allLines = inputFileHandle.readlines()

        
        inputFileHandle.close()
        
        return allLines


def readListOfListTextFile(fileURI):
    '''
    skips first line
    assumes 3 tokens in list
    '''
    allLines = loadTextFile(fileURI)
    
    allLines = allLines[1:]
    
    detectedTokenlist = []    
    for line in   allLines:  
        tokens =  line.split()
        if len(tokens) == 4:
            
            tsAndWord = [float(tokens[0]), float(tokens[1]), tokens[2], int(tokens[3])]
        else:
            tsAndWord = [float(tokens[0]), float(tokens[1]), tokens[2] ]
        
        detectedTokenlist.append(tsAndWord)
    
    return detectedTokenlist        
 
def readListOfListTextFile_gen(fileURI):
    '''
    generic
    '''
    allLines = loadTextFile(fileURI)
    
    
    tokenlist = []    
    for line in   allLines:  
        currLineTokenList = [] 

        tokens =  line.split()
        for token in tokens:
            try:
                token = float(token)
            except ValueError:
                pass
            currLineTokenList.append(token)
        tokenlist.append(currLineTokenList)
    
    return tokenlist    




def readListTextFile(fileURI):
    '''
    generic
    '''
    allLines = loadTextFile(fileURI)
    
    tokenlist = []    
    for line in   allLines:  

        token =  line.strip()
        token = float(token)
        tokenlist.append(token)
    
    return tokenlist



def writeListOfListToTextFile(detected_token_list: list, headerLine, pathToOutputFile, toFlip=False):    
    '''
    write output to file. 
    Reduce code redundancy: call writeCsv inside or merge the two methods
    :params detected_token_list: list [list [str]] 
    '''
    
    outputFileHandle = codecs.open(pathToOutputFile, 'w', 'latin-1')
    csvWriter = csv.writer(outputFileHandle, delimiter='\t')
    if not headerLine == None:
        csvWriter.write(headerLine)
    
    # flip (transpose) matrix
    if toFlip:
        a = numpy.rot90(detected_token_list)
        detected_token_list = numpy.flipud(a)
    
    counter_cons_dots = 0 # consecutive dots
    for detected_token in detected_token_list:
        
        if ParametersAlgo.DETECTION_TOKEN_LEVEL == 'syllables': # deprecated
            for element in detected_token:
                    outputSyllables(element, csvWriter)
        
        else: # words or lines 
            if  ParametersAlgo.DETECTION_TOKEN_LEVEL == 'words':
                if detected_token.text == '': # . is a special token meaning non-vocal interval detected
                    if ParametersAlgo.STORE_DOTS: 
                        detected_token.text = '.'
                    counter_cons_dots +=1 # counter
                else: # not a dot,  so reset counter
                    counter_cons_dots = 0 
            detected_token = detected_token.to_list()
            if counter_cons_dots > 1: # do not store consecutive empty spaces (dots)  
                continue
            csvWriter.writerow(detected_token)
                
    outputFileHandle.close()
    
    logger.info ("successfully written file: \n {} \n".format( pathToOutputFile))


def outputSyllables(syllable, writer):
    '''
    print a line of syllable + timestamps
    '''
    if len(syllable) < 3:
        sys.exit(' a syllable has less than the minimum 3 tokens')
#     writer.writerow(syllable[:-1]) # in format for     http://www.music-ir.org/mirex/wiki/2017:Automatic_Lyrics-to-Audio_Alignment
    
    if  syllable[2] == 'REST':
        syll_txt = '.'
    else:
        syll_txt = syllable[2]
    writer.writerow([ syll_txt, syllable[0] ]) # in format for http://sangatgracenote.github.io/lyric.html 



##################################################################################
def writeTextToTextFile(inputText, pathToOutputFile):
    '''
    dump input text to file witout any formatting
    '''    
    outputFileHandle = codecs.open(pathToOutputFile, 'w', 'utf-8')
    
    
    outputFileHandle.write(inputText)
    
    outputFileHandle.close()




##################################################################################
def writeListToTextFile(inputList,headerLine, pathToOutputFile):    
    outputFileHandle = codecs.open(pathToOutputFile, 'w', 'utf-8')
    
    if not headerLine == None:
        outputFileHandle.write(headerLine)
    
    for listLine in inputList:
        listLine = str(listLine) + '\n'
        outputFileHandle.write(listLine)
    
    outputFileHandle.close()
    logger.info ("successfully written file: \n {} \n".format( pathToOutputFile))



def write_decoded_to_file(detectedTokenList, detectedAlignedfileName,   phiOptPath=None, recording_phi_segments = None):
        '''
        writes path and list of aligned tokens to txt file 
        '''
        
        if type(detectedTokenList) == 'str': # it is an error message 
            logging.warning(detectedTokenList)
            sys.exit(detectedTokenList)
        
        # write to json
#         with open(detectedAlignedfileName + '.json', 'w') as f1:
#             json.dump(detectedTokenList, f1) 
        
        # write to tsv or so called .lab file
#         writeListOfListToTextFile(detectedTokenList, 'startTs \t endTs \t phonemeOrSyllorWord \t beginNoteNumber \n', tokenAlignedfileName)
        writeListOfListToTextFile(detectedTokenList, None, detectedAlignedfileName)
        
        # write phi (likelihood of path) to json
        if phiOptPath is not None:
            from csv import writer
            with open(detectedAlignedfileName[:-7] + 'conf.txt', 'w') as f:
                w = writer(f, delimiter='\t')
                w.writerow(['TOTAL', format(phiOptPath, '.3f')])
                for recording_phi_segment in recording_phi_segments:
                    w.writerow( [recording_phi_segment[0], format(recording_phi_segment[1],'.3f') ] )

def determineSuffix(withDuration, withOracle, withOracleOnsets, decodedTokenLevel, obs_model, q_weight_transition):
    '''
    The suffix of aligned file depends on the method, obsevation model, etc.
    '''
    
    tokenAlignedSuffix = '.'
    tokenAlignedSuffix += decodedTokenLevel
    if ParametersAlgo.DECODE_WITH_HTK:
        tokenAlignedSuffix += '_htk_'
    else:
        if withDuration: tokenAlignedSuffix += 'Duration'
        if withOracle == 1: tokenAlignedSuffix += 'OraclePhonemes'
        elif withOracle == -1: tokenAlignedSuffix += 'NoPhonemes'
        if withOracleOnsets == 1: 
            tokenAlignedSuffix += 'OracleOnsets'
            tokenAlignedSuffix += str(q_weight_transition) 
        elif withOracleOnsets == 0:
            tokenAlignedSuffix += 'Onsets'
            tokenAlignedSuffix += str(q_weight_transition)
        
        
        if obs_model == 'MLP': tokenAlignedSuffix += 'MLP'
        if obs_model == 'MLP_fuzzy': tokenAlignedSuffix += 'MLP_fuzzy'
    
            
    
    tokenAlignedSuffix += 'Aligned' 
    return tokenAlignedSuffix


def read_decoded(URIRecordingChunkResynthesizedNoExt, detectedAlignedfileName):
        '''
        read detected token list and path from file
        '''
        print("{}\n already exists. No decoding".format(detectedAlignedfileName)) 
        with open(detectedAlignedfileName, 'r') as f2:
            try:
                detectedTokenList = json.load(f2)
            except: # not json format
                detectedTokenList = readListOfListTextFile_gen(detectedAlignedfileName)
                 
        if ParametersAlgo.WITH_ORACLE_PHONEMES:
            outputURI = URIRecordingChunkResynthesizedNoExt + '.path_oracle'
        else:
            outputURI = URIRecordingChunkResynthesizedNoExt + '.path'
        
        detectedPath = ''
        if os.path.exists(outputURI):
            detectedPath = readListTextFile(outputURI) # replace by read with csv
        
        phiOptPath = '' # TODO: read with json
        return detectedTokenList, phiOptPath, detectedPath

  
    ########### statistics on a array
def getMeanAndStDevError(alignmentErrors):
        
        # convert to numpy array
        absalignmentErrors = [0] * len(alignmentErrors)
        for index, alError in enumerate(alignmentErrors):
            absalignmentErrors[index] = abs(alError)
        
        mean = numpy.round(numpy.mean(absalignmentErrors), decimals=2)
        median = numpy.round( numpy.median(absalignmentErrors), decimals=2)
        stDev = numpy.round( numpy.std(alignmentErrors), decimals=2)
        
        return mean, stDev, median
    
    
def getSectionNumberFromName(URIrecordingNoExt):
    '''
    infer which section number form score is needed by the *_2_meyan_* in the file name
    '''
    underScoreTokens  = URIrecordingNoExt.split("_")
    index = -1
    while (-1 * index) <= len(underScoreTokens):
        token = str(underScoreTokens[index])
        if token.startswith('meyan') or token.startswith('zemin') or   token.startswith('gazel') or \
        token.startswith('nakarat') or token.startswith('aranagme') or  token.startswith('taksim')  :
            break
        index -=1
    
    try:
        whichSection = underScoreTokens[index-1]
    except Exception:
        sys.exit("please put the number of section before its name: e.g. *_2_meyan_* in the file name ")
    
    URIWholeRecordingNoExt = ''
    lenTokensAudioName = len(underScoreTokens) + index - 1
    for i in range(lenTokensAudioName):
        URIWholeRecordingNoExt += underScoreTokens[i]
        if i != lenTokensAudioName - 1:
            URIWholeRecordingNoExt += '_' 

    return int(whichSection), URIWholeRecordingNoExt

def getMelodicStructFromName(URIrecordingNoExt):
    underScoreTokens  = URIrecordingNoExt.split("_")
    index = -1
    while (-1 * index) <= len(underScoreTokens):
        token = str(underScoreTokens[index])
        if token.startswith('from') :
            break
        index -=1
        
    URIWholeRecordingNoExt = ''    
    lenTokensAudioName = len(underScoreTokens) + index - 1
    for i in range(lenTokensAudioName):
        URIWholeRecordingNoExt += underScoreTokens[i]
        if i != lenTokensAudioName - 1:
            URIWholeRecordingNoExt += '_' 

    
    
    return   underScoreTokens[index-1], URIWholeRecordingNoExt


def getBeginTsFromName(URIrecordingNoExt):
    '''
    infer which section number form score is needed by the *_2_meyan_* in the file name
    '''
    underScoreTokens  = URIrecordingNoExt.split("_")
    index = -1
    while (-1 * index) <= len(underScoreTokens):
        token = str(underScoreTokens[index])
        if token.startswith('from') :
            break
        index -=1
    
    try:
        startTsBase = underScoreTokens[index+1]
        startTsRemainder = underScoreTokens[index+2]
        startTs = startTsBase + '.' + startTsRemainder
    except Exception:
        sys.exit("no from or no number ts  it")
   
    return float(startTs)

def getEndTsFromName(URIrecordingNoExt):
    '''
    infer which section number form score is needed by the *_2_meyan_* in the file name
    '''
    underScoreTokens  = URIrecordingNoExt.split("_")
    index = -1
    while (-1 * index) <= len(underScoreTokens):
        token = str(underScoreTokens[index])
        if token.startswith('to') :
            break
        index -=1
    
    try:
        endTsBase = underScoreTokens[index+1]
        startTsRemainder = underScoreTokens[index+2]
        endTs = endTsBase + '.' + startTsRemainder
    except Exception:
        sys.exit("no from or no number ts  it")
   
    return float(endTs)


def getBeginTsFromNameJingju(URIrecordingNoExt):
    '''
    infer from the file name is begining timestamp
    '''
    underScoreTokens  = URIrecordingNoExt.split("_")
    endTs = underScoreTokens[-1]
    startTs = underScoreTokens[-2]
    
    return float(startTs), float(endTs)


def renameFilesInDir(argv):
    '''
    renameSectionIndices in a dir with extension e.g. TextGrid
    use method renameSectionIndex
    '''
    if len(argv) != 4:
        sys.exit("usage: {} <dirURI> <extension> <new file Name>".format(argv[0]))
    
    dirURI = argv[1]
    extension = argv[2]
    listExtensions = [extension]
    newFileName = argv[3]
    
    fileNames = findFileByExtensions(dirURI, listExtensions)
    
    for fileName in fileNames:
        fileURI = os.path.join(dirURI, fileName)
        renameSectionIndex2(fileURI, newFileName)
        
    
    
# rename
    
    

def renameSectionIndex(URIrecording):
    '''
    rename. change number of score section to another number. Needed if score sections are renumbered in sections.tsv/json file/
    NOTE: could be changed for other renaming purposes accordingly 
    '''
    underScoreTokens  = URIrecording.split("_")
    index = -1
    found = False
#     check array in reverse order 
    while (-1 * index) <= len(underScoreTokens):
        token = str(underScoreTokens[index])
        if token.startswith('meyan') or token.startswith('zemin') or   token.startswith('gazel') or \
        token.startswith('nakarat') or token.startswith('aranagme') or  token.startswith('taksim')  :
            found = True
            break
        # decrement
        index -= 1
    if not found:
        sys.exit("please put the number of section before its name: e.g. *_2_meyan_* in the file name ") 
    
    print(index)
    sectionIndex = int(underScoreTokens[index-1]) 
    sectionIndex += 1
    underScoreTokens[index-1] = str(sectionIndex)
    newURIrecording = "_".join(underScoreTokens)
    print(newURIrecording)
    
    try:
        os.rename(URIrecording, newURIrecording)
        logger.info("renaming {} to {}".format(URIrecording, newURIrecording)) 
    except Exception as error:
        print(str(error))

def renameSectionIndex2(URIrecording, newName):
    '''
    rename. change name of TextGrid file with old naming to new naming of autoamtically fetched file from dunya.get_mp3_recording.
    NOTE: could be changed for other renaming purposes accordingly 
    '''
    underScoreTokens  = URIrecording.split("_")
    index = -1
    found = False
#     check array in reverse order 
    while (-1 * index) <= len(underScoreTokens):
        token = str(underScoreTokens[index])
        if token.startswith('meyan') or token.startswith('zemin') or   token.startswith('gazel') or \
        token.startswith('nakarat') or token.startswith('aranagme') or  token.startswith('taksim')  :
            found = True
            break
        # decrement
        index -= 1
    if not found:
        sys.exit("please put the number of section before its name: e.g. *_2_meyan_* in the file name ") 
    
    print(index)
    sectionIndex = int(underScoreTokens[index+2]) 
#     sectionIndex += 1
    
    newURIrecording = newName + '_' + underScoreTokens[index+2] + '.' + underScoreTokens[index+3]  + '_' +  underScoreTokens[index+5] + '.' + underScoreTokens[index+6]   
    print(newURIrecording)
    
    try:
        os.rename(URIrecording, newURIrecording)
        logger.info("renaming {} to {}".format(URIrecording, newURIrecording)) 
    except Exception as error:
        print(str(error))



def addTimeShift( listTsAndTokens,   timeShift=0):
    '''
    convenience method.
    add given shift to list of tokens 
    '''
    
    for token in listTsAndTokens:
          
        if ParametersAlgo.DETECTION_TOKEN_LEVEL == 'syllables': # deprecated
            for index in range(len(token)):
                token[index][0] +=  timeShift # begin Ts
                token[index][1] +=  timeShift
        
        else: # words, lines, phonemes
            token.start_ts = float('{:.2f}'.format(token.start_ts + timeShift))  
            if hasattr(token,'end_ts'):
                token.end_ts =   float('{:.2f}'.format(token.end_ts + timeShift)) 
                 
#     logging.debug('phoneme level alignment written to file: ',  phonemeAlignedfileName)
    return listTsAndTokens


def fetchFileFromURL(URL, outputFileURI):
#         print "fetching file from URL {}...".format(URL)
        
        try:
            import urllib.request
            response = urllib.request.urlopen(URL)
            a = response.read()
        except:
            sys.exit('Could not retrieve important data. Check your internet connection!')
        with open(outputFileURI,'w') as f:
            f.write(a)
        
def fetch_string_fromURL(URL):
#         print "fetching file from URL {}...".format(URL)
            
        try:
            import urllib.request
            response = urllib.request.urlopen(URL)
            a = response.read()
        except:
            sys.exit('Could not retrieve important data. Check your internet connection!')
        return a

        

def readLookupTable(URItable):
        '''
        read lookup table from file
        '''

        lookupTableRaw = loadTextFile(URItable)
        lookupTable = dict()
        for lineTable in lookupTableRaw:
            tokens = lineTable.split("\t")
            grapheme = tokens[0]
            if not isinstance(grapheme, str):
                    grapheme = str(grapheme,'utf-8')
            #non-ascii represented by digit. becasue table is reuse din matlab, who does not understand utf 
            if len(grapheme) == 4 and grapheme[0].isdigit(): 
                grapheme = "\\u" + grapheme
                grapheme = grapheme.decode('unicode-escape')
            
            # one-to-one
            if len(tokens) == 2:
                phonemeTokens = tokens[1].rstrip().split()
                
                if len(phonemeTokens) == 1:
                    lookupTable[grapheme] = phonemeTokens[0]
                elif len(phonemeTokens) == 0:
                    lookupTable[grapheme] = tokens[1].rstrip()

#              one-to-more, more are separated by space
                else:
                    lookupTable[grapheme] = phonemeTokens 
            
            # one-to-more
            elif  len(tokens) > 2:
                phonemes = []
                for phonemeCurr in tokens[1:]:
                    phonemes.append(phonemeCurr.strip())  
                
                lookupTable[grapheme] = phonemes

        return lookupTable




def tsToFrameNumber(ts):
    '''
    get which frame is for a given ts, according to the timing of htk's feature extraction  
    '''
    if ParametersAlgo.MFCC_HTK:
        return   max (0, int(math.floor( (ts - ParametersAlgo.WINDOW_LENGTH/2.0) * ParametersAlgo.NUMFRAMESPERSECOND)) )
    else:
        msg = 'tsToFrameNumber : if extracted mfcc features with s.th. different from htk, not implemented!'
        raise RuntimeError(msg)
 
 
def frameNumberToTs(frameNum):
    '''
    get which ts is for a given frame, according to htk's feature extraction  
    '''
    return float(frameNum) /    float(ParametersAlgo.NUMFRAMESPERSECOND) + ParametersAlgo.WINDOW_LENGTH/2.0



if __name__ == '__main__':
# test some functionality
    renameFilesInDir(sys.argv)
#        tokenList =  readListOfListTextFile('nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi/Melihat_Gulses/Melihat_Gulses_2_zemin_from_47_355984_to_68_789494.phrasesDurationSynthAligned')