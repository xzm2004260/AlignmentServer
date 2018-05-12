'''
Created on Apr 27, 2016

@author: joro
'''

### include src folder
import os
import sys
import collections

from src.align.ParametersAlgo import ParametersAlgo

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if parentDir not in sys.path:
    sys.path.append(parentDir)
    
from src.utilsLyrics.Utilz import readLookupTable


class Phonetizer(object):
    phoneticDict = dict() # METUBet or x-sampa phonetic dictionary
    phoneticDict_CMU = None
    withAccompaniment = 0
    
    @staticmethod
    def initPhoneticDict(withAccompaniment, URI_phonetic_dict):
        '''
        load the phonetic dictionary ( METUbet for Turkish or CMU dict for English)
        '''
        # if not yet created:
        if not Phonetizer.phoneticDict:
            Phonetizer.withAccompaniment = withAccompaniment

            if ParametersAlgo.FOR_MAKAM:
                Phonetizer.phoneticDict = readLookupTable(URI_phonetic_dict)
            elif ParametersAlgo.FOR_JINGJU: 
                # for now it does not distinguish bt/w a cappella and poly
                Phonetizer.phoneticDict = readLookupTable(URI_phonetic_dict)
            
            else: # English
                # for now it does not distinguish bt/w a cappella and poly
                Phonetizer.phoneticDict = read_cmu_dict(URI_phonetic_dict)
        
def read_cmu_dict(fn):
    lex = collections.defaultdict(list)

    with open(fn, 'r') as fh:
        for ln in fh:
            ln = ln.strip();

            if ln == '':
                continue

            parse_cmu_dict_line(ln, lex)

    return lex

def parse_cmu_dict_line(ln, lex):
    ortho, phone = ln.split(None, 1)

    # normalize orthography
    ortho = ortho.lower()
    if any([ortho.endswith('({})'.format(i)) for i in range(1, 10)]):
        ortho = ortho[0:-3]  # strip (1), (2), .., (9)

    # normalize transcription
    phone = phone.lower()
    sylls = [syll.strip() for syll in phone.split('-')]
    stresses = [0]*len(sylls)
    for k in range(len(sylls)):
        phns = sylls[k].split()
        stress = 0  # no stress
        if any([phn.endswith('2') for phn in phns]):
            stress = 2  # secondary stress
        if any([phn.endswith('1') for phn in phns]):
            stress = 1  # primary stress
        phns = [phn.rstrip('012') if phn != 'ah0' else 'ax' for phn in phns]  # strip stress and change ah0 to ax
        sylls[k] = ' '.join(phns)
        stresses[k] = stress

    # store
    lex[ortho].append(list(zip(sylls, stresses)))