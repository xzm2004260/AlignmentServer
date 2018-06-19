import os
import sys
import numpy
from test.test_load_lyrics import setUp_recording

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

testDir = os.path.dirname(os.path.realpath(__file__))

from .test_backtrack import run_backtrack
from src.align.ParametersAlgo import ParametersAlgo

ParametersAlgo.FOR_MAKAM = 0
ParametersAlgo.FOR_JINGJU = 0
ParametersAlgo.POLYPHONIC = 0

def test_get_segment_path():
    '''
    test getting the indices of the elements for a segment from decoded path
    '''

    
    recording = setUp_recording(with_section_annotations=0)
    
    # actual conversion
    path = run_backtrack()
    # TODO: load hmm.Path object from the correct results of test_BackTrack(), see https://github.com/georgid/AlignmentMagix/issues/3
#     with open('persistent/path.json', 'r') as f:
#        path_raw = json.load(f)
    
    recording.sectionLinks[0].createLyricsModels()
    start_word_indices = [0,2]
    end_word_indices = [-2,-1]
    reference_results = [ (0, 28, 0, 399), (9,30,188,401) ]
    for start_word_idx, end_word_idx, ref_result in zip(start_word_indices, end_word_indices, reference_results):
        lyricsWithModels = recording.sectionLinks[0].lyricsWithModels
        idx_begin_state, idx_end_state, begin_frame, end_frame = path.get_segment_indices(lyricsWithModels, start_word_idx, end_word_idx)
        assert ref_result == (idx_begin_state, idx_end_state, begin_frame, end_frame)
    
def test_calc_phi_indices():
    '''
    test the calculation of a confidence measure phi for all lines of lyrics
    '''

    recording = setUp_recording(with_section_annotations=0)

    # actual conversion
    path = run_backtrack()

    section_link = recording.sectionLinks[0]
    section_link.createLyricsModels()

    absPathPhi = os.path.join(testDir, 'persistent/phi_umbrella_line.txt' )
    phi = numpy.loadtxt(absPathPhi)

    phi_segments = path.calc_phi_segments_lines(phi, section_link.lyricsWithModels)
    assert phi_segments == [0.7212969967349567]
    
if __name__ == '__main__':
    test_calc_phi_indices()
