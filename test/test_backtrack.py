import os
import numpy
import json
import sys


projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

from src.align.ParametersAlgo import ParametersAlgo
from src.hmm.Path import Path
from src.utilsLyrics.UtilzNumpy import assertListsEqual

testDir = os.path.dirname(os.path.realpath(__file__))


def run_backtrack():
    '''
    helper method: load phi and psi, create a Path object and backtrack
    '''
    absPathPsi = os.path.join(testDir, 'persistent/psi_umbrella_line.txt' )
    psiBackPointer = numpy.loadtxt(absPathPsi)

    
    if ParametersAlgo.WITH_DURATIONS: path = None # TODO
    else: path =  Path( psiBackPointer)
    
    return path

def test_BackTrack():  
    
    path = run_backtrack()
#     print "path is {}".format(path.pathRaw)
    
    URI_persistent_path = os.path.join(testDir, 'persistent/path_umbrella_line.json')
    
#     with open(URI_persistent_path, 'w') as f:
#         json.dump(path.pathRaw.tolist(), f )
       
#     with open('persistent/state_indices_umbrella_line.json', 'w') as f:
#        json.dump(path.indicesStateStarts, f )

    with open(URI_persistent_path, 'r') as f:
        path_persistent = json.load(f)
    assertListsEqual(path_persistent, path.pathRaw)
    