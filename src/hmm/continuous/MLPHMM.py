'''
Created on Nov 12, 2015
'''

import numpy as np
import sys
import os
import math
import csv
import tempfile
import theano
from io import StringIO
import json
import time
import shutil
import logging


# Prepare readers for compressed files
readers = {}
try:
    import gzip
    readers['.gz'] = gzip.GzipFile
except ImportError:
    pass

try:
    import bz2
    readers['.bz2'] = bz2.BZ2File
except ImportError:
    pass



import pickle

    
from theano.tensor.shared_randomstreams import RandomStreams

from src.hmm.continuous._HMM import _HMM
from src.hmm.continuous._ContinuousHMM import _ContinuousHMM

from src.align.ParametersAlgo import ParametersAlgo

# sys.path.append('/home/georgid/Documents/pdnn')
currDir = os.path.abspath( os.path.join( os.path.dirname(os.path.realpath(__file__)) , os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir ) )

MODEL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.pardir, os.pardir,  'models_english/' )

pdnn_dir = os.path.join(currDir, 'pdnn/')
if pdnn_dir not in sys.path:
    sys.path.append(pdnn_dir)

# leave these imports here. dont reorder
# from io_func import smart_open
from models.dnn import DNN
# from io_func.model_io import _file2nnet


# from _ContinuousHMM import _ContinuousHMM
# class DurationGMHMM(_ContinuousHMM):
class MLPHMM(_HMM):
    '''
    A MLP HMM - This is a representation of a continuous HMM,
    containing MLP Neural Network in each hidden state.
    
    For more information, refer to _ContinuousHMM.
    '''


        
    def __init__(self, statesNetwork, model=None, cfg=None, ):
        '''
        See base class constructor for more information
        '''
        
        self.model = model
        self.cfg = cfg
        _HMM.__init__(self, statesNetwork) # create hmm network
        
        # load alphabet 
        if ParametersAlgo.FOR_MAKAM: # METUbet for Turkish
            METU_ARPA_to_stateidx_URI = os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.pardir, os.pardir,  'for_makam' , 'state_str2int_METU')
            self.phn_to_stateidx = load_METU_to_ARPA_mapping(METU_ARPA_to_stateidx_URI)
        elif ParametersAlgo.FOR_JINGJU:
            sys.exit('MLP not implmented for Jingju')
        else: # ARPABET for English
            to_stateidx_URI = os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.pardir, os.pardir,  'for_english' , 'state_str2int')
            self.phn_to_stateidx = load_ARPA(to_stateidx_URI)
            

    
    def _mapB(self, features):
        '''
        extend base method. first load all output with given MLP
        takes time, so better do it in advance to _pdfAllFeatures()
        '''
        if not ParametersAlgo.USE_PERSISTENT_PPGs or not os.path.exists(self.PATH_BMAP):
            self.logger.debug("calculating obs probs..." )
            self.mlp_posteriograms = self.recogn_with_MLP( features) ## computre posteriograms
              
        _ContinuousHMM._mapB(self, features) # , _ContinuousHMM._mapB calls _pdfAllFeatures()
        
        
    def _pdfAllFeatures(self,features,j):
        '''
        get the log likelohood of a series of features for the model that corresponds to state j.
        
        called from _Continuous._mapB()
        
        -----------------------
        Returns 
        log likelihoods p(Y_1:T | j)
        '''
#         old_settings = np.seterr(under='warn')
        
        #### get index of the model of the phoneme that corresponds to the given state j from the state sequence
        curr_phoneme_ID = self.statesNetwork[j].phoneme.ID
        if curr_phoneme_ID not in self.phn_to_stateidx:
                logging.warning('phoneme {} not in dict'.format(curr_phoneme_ID) )
                phoneme_idx = 0
        else:
            phoneme_idx = self.phn_to_stateidx[curr_phoneme_ID] # direct mapping
            

        
        probs_phoneme = self.mlp_posteriograms[:,phoneme_idx]
        return probs_phoneme
    
    

    def configure_from_faetures(self, features):
        '''
        dump current observation features to a binary file 
        and configure them 
        '''
        tmp_dir = tempfile.mkdtemp()
        tmp_obs_file = os.path.join(tmp_dir, 'features.pkl')
        labels = np.zeros(len(features), dtype='float32')
        with open(tmp_obs_file, 'wb') as f:
            pickle.dump((features, labels), f)
        self.cfg.init_data_reading_test(tmp_obs_file)
        return tmp_dir
    

    def recogn_with_MLP(self, features):
        '''
        recognize with MLP softmax model
        
        
        Parameters: 
        features 
        
        Return:
        -------------------------- 
        39-dimensional (for each phoneme from CMU's ARPA ) prob. vector, normalized to sum to one for each vector (row) 
        
        '''
        if self.model == None or self.cfg == None:
            self.model, self.cfg = load_MLPs_and_config() 
        
        time1 = time.time()

        # double check that features are in same dimension as models
        if features.shape[1] != self.model.n_ins:
                sys.exit("dimension of feature vector should be {} but is {} ".format(self.model.n_ins, features.shape[1]) )
        
        ################ recognize
        layer_index  = -1 # last tier
        batch_size = 100

        tmp_dir = self.configure_from_faetures(features)
        
        # get the function for feature extraction
        extract_func = self.model.build_extract_feat_function(layer_index)
    
        output_mats = []    # store the features for all the data in memory. TODO: output the features in a streaming mode
        while (not self.cfg.test_sets.is_finish()):  # loop over the data
            self.cfg.test_sets.load_next_partition(self.cfg.test_xy)
            batch_num = int(math.ceil(1.0 * self.cfg.test_sets.cur_frame_num / batch_size))
    
            for batch_index in range(batch_num):  # loop over mini-batches
                start_index = batch_index * batch_size
                end_index = min((batch_index+1) * batch_size, self.cfg.test_sets.cur_frame_num)  # the residue may be smaller than a mini-batch
                output = extract_func(self.cfg.test_x.get_value()[start_index:end_index])
                output_mats.append(output)
        
        shutil.rmtree(tmp_dir) # clean up tmp dir

        output_mat = np.concatenate(output_mats) 
        time2 = time.time()
        self.logger.debug(" computing obs probs with DNN model: {} seconds".format(time2-time1) )   
        return output_mat
    
    
    def _pdf(self,x,mean,covar):
        '''
        Gaussian PDF function
        '''        
        covar_det = np.linalg.det(covar);
        
        c = (1 / ( (2.0*np.pi)**(float(self.d/2.0)) * (covar_det)**(0.5)))
        pdfval = c * np.exp(-0.5 * np.dot( np.dot((x-mean),covar.I), (x-mean)) )
        return pdfval
    
    
def load_METU_to_ARPA_mapping(METU_to_stateidx_URI):
        '''
        METU phoneme corresponds to which idx in trained model 
        '''

        METU_to_stateidx = {} # dict
        
        with open(METU_to_stateidx_URI, 'rb') as csvfile:
            score_ = csv.reader(csvfile, delimiter=' ')
            for row in score_:
                    METU_to_stateidx[row[0]] = int(row[-1])
        METU_to_stateidx['Y'] = 1 # add short Y
        return METU_to_stateidx

def load_ARPA(METU_to_stateidx_URI):
        '''
        ARPA_CMU phoneme corresponds to which idx in trained model 
        '''

        ARPA_to_stateidx = {} # dict
        
        with open(METU_to_stateidx_URI, 'r') as csvfile:
            score_ = csv.reader(csvfile, delimiter=' ')
            for row in score_:
                    ARPA_to_stateidx[row[0]] = int(row[-1])
        return ARPA_to_stateidx
    
    
def _file2nnet(layers, set_layer_num = -1, file_as_string='',  filename='', factor=1.0):
    n_layers = len(layers)
    nnet_dict = {}
    if set_layer_num == -1:
        set_layer_num = n_layers

    if filename != '':
        with open(filename, 'r') as fp:
            nnet_dict = json.load(fp)
    else:
        nnet_dict = json.loads(file_as_string)
        
    for i in range(set_layer_num):
        dict_a = 'W' + str(i)
        layer = layers[i]
        if layer.type == 'fc':
            mat_shape = layer.W.get_value().shape
            layer.W.set_value(factor * np.asarray(string_2_array(nnet_dict[dict_a]), dtype=theano.config.floatX).reshape(mat_shape))
        elif layer.type == 'conv':
            filter_shape = layer.filter_shape
            W_array = layer.W.get_value()
            for next_X in range(filter_shape[0]):
                for this_X in range(filter_shape[1]):
                    new_dict_a = dict_a + ' ' + str(next_X) + ' ' + str(this_X)
                    mat_shape = W_array[next_X, this_X, :, :].shape
                    W_array[next_X, this_X, :, :] = factor * np.asarray(string_2_array(nnet_dict[new_dict_a]), dtype=theano.config.floatX).reshape(mat_shape)
            layer.W.set_value(W_array)
        dict_a = 'b' + str(i)
        layer.b.set_value(np.asarray(string_2_array(nnet_dict[dict_a]), dtype=theano.config.floatX))

def string_2_array(string):
    str_in = StringIO(string)
    array_tmp = np.loadtxt(str_in)
    if len(array_tmp.shape) == 0:
        return np.array([array_tmp])
    return array_tmp


def load_MLPs_and_config():
    '''
    load the MLP learned model as MLP network  
    '''
    file_as_string = ''
    filename = ''
#         file_as_string = fetch_string_fromURL('https://drive.google.com/uc?authuser=0&id=12ihD4dUz74Q3VKTpp3doMk6-pgL9rUGt&export=download') 
    filename = os.path.join(MODEL_PATH,   'bsoot.fas') # one this or previous line
    nnet_cfg = os.path.join(MODEL_PATH, 'pnak.cfg')

    
    numpy_rng = np.random.RandomState(89677)
    theano_rng = RandomStreams(numpy_rng.randint(2 ** 30))
#     cfg = pickle.load(smart_open(nnet_cfg,'r'))
    cfg = pickle.load(open(nnet_cfg,'rb'))
    cfg.init_activation()
    
    
    model = DNN(numpy_rng=numpy_rng, theano_rng = theano_rng, cfg = cfg)

    # load model parameters
    _file2nnet(model.layers, file_as_string=file_as_string,  filename=filename) # this is very slow
    
    return model, cfg


def smart_open(filename, mode = 'rb', *args, **kwargs):
    '''
    Opens a file "smartly":
      * If the filename has a ".gz" or ".bz2" extension, compression is handled
        automatically;
      * If the file is to be read and does not exist, corresponding files with
        a ".gz" or ".bz2" extension will be attempted.
    (The Python packages "gzip" and "bz2" must be installed to deal with the
        corresponding extensions)
    '''
    if 'r' in mode and not os.path.exists(filename):
        for ext in readers:
            if os.path.exists(filename + ext):
                filename += ext
                break
    extension = os.path.splitext(filename)[1]
    return readers.get(extension, open)(filename, mode, *args, **kwargs)

