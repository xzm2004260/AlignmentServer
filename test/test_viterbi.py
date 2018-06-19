'''
Created on Jan 23, 2018

@author: joro
'''
import numpy as np
import essentia.standard as es
import os



testDir = os.path.dirname(os.path.realpath(__file__))
    

def tes_viterbi_essentia():
    '''
    tests if output of Viterbi (non-forced) with essentia is the same as with python forced 
    '''
    trans_matrix = np.loadtxt(os.path.join(testDir,'persistent/trans_matrix_umbrella_line.txt')) # stored in log domain
    B_map = np.loadtxt(os.path.join(testDir,'persistent/B_map_umbrella_line.txt')) # stored in log domain
    pi = np.loadtxt(os.path.join(testDir,'persistent/pi_umbrella_line.txt'))
    
    esViterbi = es.Viterbi(forcedAlignment=1)
        
    trans_matrix_ = es.essentia.array(trans_matrix)
    B_map_ = es.essentia.array(B_map)
    pi_ = es.essentia.array(pi)
    (phi_, psi_) = esViterbi(trans_matrix_, B_map_, pi_)
    
    
#     np.savetxt('persistent/psi_ess_umbrella_line.txt', psi_.T)
    # computed with python with input
    test_phi = np.loadtxt(os.path.join(testDir, 'persistent/phi_umbrella_line.txt'))
    test_psi = np.loadtxt(os.path.join(testDir,'persistent/psi_umbrella_line.txt'))  


#     visualize difference 
#     arr_diff = abs(test_psi  - psi_.T)
#     visualizeMatrix(arr_diff, 'diff psi')
# 
#     arr_diff = abs(test_phi  - phi_.T)
#     visualizeMatrix(arr_diff, 'diff phi')
        
    assert np.allclose(psi_.T, test_psi, atol=1e-03) 
    assert np.allclose(phi_.T, test_phi, atol=1e-03)
     

def visualizeMatrix(psi,  titleName):
    
        import matplotlib.pylab as plt
        import matplotlib
        fig, ax1 = plt.subplots()
        ax  = plt.imshow(psi, interpolation='none', aspect='auto')
        plt.colorbar(ax)
        plt.grid(True)
        plt.title(titleName)
        figManager = plt.get_current_fig_manager()
        figManager.full_screen_toggle()
        
        matplotlib.rcParams.update({'font.size': 22})
#         plt.tight_layout()
        
        plt.show() 
        return ax1 

        
if __name__ == '__main__':
    test_viterbi_essentia()
    