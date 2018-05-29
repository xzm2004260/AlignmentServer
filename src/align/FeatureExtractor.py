'''
Created on May 27, 2015

@author: joro
'''
import numpy as np
import logging

import math
import subprocess
import os
import sys
import scipy.signal

# from essentia.standard import PredominantPitchMelodia

### include src folder

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir, os.path.pardir)) 

from src.align.ParametersAlgo import ParametersAlgo


# pathSMS = os.path.join(parentDir, 'sms-tools')
# print '\n sys.path:' + sys.path +  '\n'
# if pathSMS not in sys.path:
#     sys.path.append(pathSMS)



MODEL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.pardir,  'models_english/' )


projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.path.pardir ))
parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

currentPath = os.path.dirname(__file__)
parentDir = os.path.join(currentPath , os.path.pardir, os.path.pardir, os.path.pardir )

if ParametersAlgo.FOR_JINGJU:
    jingjuPhraseDir = os.path.join(parentDir, 'jingjuSingingPhraseMatching/phoneticSimilarity/')
    if jingjuPhraseDir not in sys.path: sys.path.append(jingjuPhraseDir)
    
    jingjuPhraseDir2 = os.path.join(parentDir, 'jingjuSingingPhraseMatching/')
    if jingjuPhraseDir2 not in sys.path: sys.path.append(jingjuPhraseDir2)
    
    from targetAudioProcessing import processFeature



PREEMPH = 0.97 # preemphasis's default value in htk
HIGH_FREQ_BOUND = 8000 #hard coded in htk's config file, too


class FeatureExtractor(object):
    def __init__(self, path_to_hcopy=None, sectionLink=None):
        if path_to_hcopy is not None:
            self.path_to_hcopy = path_to_hcopy
        if sectionLink is not None:
            self.featureVectors = []
        
        self.logger = logging.getLogger(__name__)
        # other logger set in decoder 
        loggingLevel = ParametersAlgo.LOGGING_LEVEL
#         loggingLevel = logging.INFO
#         loggingLevel = logging.WARNING

        self.logger.setLevel(loggingLevel)
   
   




    def loadMFCCs(self, audio, currSectionLink, sampleRate): 
        '''
        extract mfccs
        
        TODO: describe what is a section link 
        
        '''
        if sampleRate < 2* HIGH_FREQ_BOUND:
            sys.exit( 'extracting features with higher bound {} needs sampling rate of at least {}. Sampling rate of {} detected  instead. ' \
            .format(HIGH_FREQ_BOUND, 2* HIGH_FREQ_BOUND, sampleRate) )
        
        URI_recording_tmp = currSectionLink.URIRecordingChunk + '.wav'
        begin_sample = int(currSectionLink.beginTs * sampleRate)
        end_sample = int(currSectionLink.endTs * sampleRate)
        audio = audio[begin_sample : end_sample] 
        
        # call htk to extract features
        if ParametersAlgo.MFCC_HTK:
#             scipy.io.wavfile.write(filename=URI_recording_tmp, rate=sampleRate, data=(audio).astype('int16')) # write back to file, because htk needs to read a file
            mfccsFeatrues = self._extractMFCCs_htk( URI_recording_tmp)
#             os.remove(URI_recording_tmp)
            
        else: # with essentia 
            self.logger.info("extracting mfccs with C++ for recording: {} ...".format(URI_recording_tmp))
            mfccsFeatrues = self._extractMFCCs( URI_recording_tmp, audio, sampleRate) # audio in the case of a cappella
            # TODO: here recording
        
        # it should be removed only in production env.
#         os.remove(URI_Segment) # remove audio for segment after extracting features
        
        
        return mfccsFeatrues
    
    
    def _extractMFCCs(self, filename, audio, sampleRate):
        '''
        Extract mfcc (htk type) with essentia
        
        Reproduces the htk type extracted with one of the configuratins:
        ../src/models_makam/input_files/wav_config_default
    
        for visualisation see https://github.com/georgid/mfcc-htk-an-librosa/blob/master/mfcc-htk-many-parameters.py
        Parameters
        --------------
        filename:
            name of audio segment (chunk) as wav file to be processed
        
        '''
        import essentia
        import essentia.standard as ess
        
        if ParametersAlgo.OBS_MODEL == 'MLP':  
                if ParametersAlgo.FOR_JINGJU:
                    # reproduce /models_makam/input_files/wav_config_singing_yile # no singal amplitude normalization
                    sys.exit('not implemented with essentia')
                elif ParametersAlgo.FOR_MAKAM:
                    # reproduce /models_makam/input_files/wav_config_singing_makam
                    sys.exit('not implemented with essentia')
        
        elif ParametersAlgo.OBS_MODEL == 'CNN': # mfcc type based on the model trained with these for mandarin
            if not os.path.isfile(filename):
                sys.exit('OBS_MODEL CNN desired but no audio file {} exists'.format(filename) )
            return processFeature(filename, feature_type='mfccBands2D')

        audio = essentia.array(audio) # make sure compatible with essentia

        # dynamic range expansion as done in HTK implementation
        audio = audio*2**15
    
        frameSize = int(math.floor(float(ParametersAlgo.WINDOW_LENGTH) * float(sampleRate))) # will be 1102 for WINDOWLENGTH = 250000.0 at fs=44100 
        hopSize = int(math.floor(float(sampleRate) / float(ParametersAlgo.NUMFRAMESPERSECOND) )) # will be 441 if NUMFRAMESPERSECOND = 100 

        fftSize = next_power_of_two(frameSize) # next power of two >=  frameSize . 2048 if fs=44100 
        spectrumSize= fftSize//2+1
        zeroPadding = fftSize - frameSize
    
        w = ess.Windowing(type = 'hamming', #  corresponds to htk default  USEHAMMING = T
                            size = frameSize, 
                            zeroPadding = zeroPadding,
                            normalized = False,
                            zeroPhase = False)
    
        spectrum = ess.Spectrum(size = fftSize)
    
        mfcc_htk = ess.MFCC(inputSize = spectrumSize,
                            type = 'magnitude', # htk uses mel filterbank magniude
                            warpingFormula = 'htkMel', # htk's mel warping formula
                            weighting = 'linear', # computation of filter weights done in Hz domain
                            highFrequencyBound = HIGH_FREQ_BOUND, # corresponds to htk default
                            lowFrequencyBound = 0, # corresponds to htk default
                            numberBands = 26, # corresponds to htk default  NUMCHANS = 26
                            numberCoefficients = 13,
                            normalize = 'unit_max', # htk filter normaliation to have constant height = 1  
                            dctType = 3, # htk uses DCT type III
                            logType = 'log',
                            liftering = 22) # corresponds to htk default CEPLIFTER = 22
    
    
        mfccs = []
        
        preemph_filter = ess.IIR(numerator=[1-PREEMPH])

        # startFromZero = True, validFrameThresholdRatio = 1 : the way htk computes windows
        for i, frame in enumerate(ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize , startFromZero = True, validFrameThresholdRatio = 1) ):
            if PREEMPH != 0: ##### corresponds to PREEMCOEF = 0.97 in htk
                frame_doubled_first = np.insert(frame,0,frame[0])  
                preemph_frame = preemph_filter(frame_doubled_first)
                frame = preemph_frame[1:]
            frame = preemph(frame, PREEMPH)
            
            spect = spectrum(w(frame))
            mel_bands, mfcc_coeffs = mfcc_htk(spect)
            
            if np.isnan(mfcc_coeffs).any():
                self.logger.debug('frame  {} has nans'.format(i) )
                mfcc_coeffs = np.nan_to_num(mfcc_coeffs) # workaround for NaNs -> to zero
            
            mfccs.append(mfcc_coeffs)
        
        essMFCC = essentia.array(mfccs).T # transpose to (d,t) dimension, which is used by librosa 
        essMFCC = essMFCC[[1,2,3,4,5,6,7,8,9,10,11,12,0],:] # move energy at the end as it is in htk _0
        
        ###  deltas and accelerations with librosa. corresponds to _D and _A in htk
#         delta_mfcc = librosa.feature.delta(essMFCC)
#         delta_delta_mfcc = librosa.feature.delta(essMFCC, order=2)
        delta_mfcc = delta(essMFCC)
        delta_delta_mfcc = delta(essMFCC, order=2)

        essMFCC = np.vstack((essMFCC, delta_mfcc))
        essMFCC = np.vstack((essMFCC, delta_delta_mfcc))

        # cepstral zero-mean.  correposnds to _Z in htk
        essMFCC  = np.matrix(essMFCC)
        means = essMFCC.mean(axis=1)
        essMFCC = essMFCC - means
        
        essMFCC = essentia.array(essMFCC).T # transpose back
        return essMFCC
            
    def _extractMFCCs_htk( self, URIRecordingChunk):
            '''
            Extract mfcc (htk type) with htk
            '''
            import src.align.htkmfc as htkmfc

            baseNameAudioFile = os.path.splitext(os.path.basename(URIRecordingChunk))[0]
            dir_ = os.path.dirname(URIRecordingChunk)
#             dir_  = tempfile.mkdtemp()
            URImfcFile = os.path.join(dir_, baseNameAudioFile  ) + '.mfc'
            
            if ParametersAlgo.OBS_MODEL == 'MLP' or ParametersAlgo.OBS_MODEL == 'MLP_fuzzy': # only one type of features trained
               PATH_TO_CONFIG_FEATURES = os.path.join(MODEL_PATH, 'tost.cf' )
            elif  ParametersAlgo.OBS_MODEL == 'GMM':  
                if ParametersAlgo.FOR_JINGJU:
                    PATH_TO_CONFIG_FEATURES = projDir + '/models_makam/input_files/wav_config_singing_yile' # no singal amplitude normalization
    
                elif ParametersAlgo.FOR_MAKAM:
                    PATH_TO_CONFIG_FEATURES = projDir + '/models_makam/input_files/wav_config_singing_makam'
                
            
#             HCopyCommand = [self.path_to_hcopy, '-A', '-D', '-T', '1', '-C', PATH_TO_CONFIG_FEATURES, URIRecordingChunk, URImfcFile]
            HCopyCommand = [self.path_to_hcopy, '-C', PATH_TO_CONFIG_FEATURES, URIRecordingChunk, URImfcFile]
    
            if not os.path.isfile(URImfcFile):
                self.logger.info(" Extracting mfcc with htk command: {}".format( subprocess.list2cmdline(HCopyCommand) ) )
                try:
                    pipe= subprocess.Popen(HCopyCommand)
                    pipe.wait()
                except:
                    sys.exit('mfcc features could not be extracted. check if  htk is properly installed and its path is set correctly (s.th.like /usr/local/bin/HCopy)   ')
            
            # read features form binary htk file
            self.logger.debug("reading MFCCs from {} ...".format(URImfcFile))
            HTKFeat_reader =  htkmfc.open_file(URImfcFile, 'rb') # htkmfc.open
            mfccsFeatrues = HTKFeat_reader.getall()
            os.remove(URImfcFile)
            
            return mfccsFeatrues
        

def getTimeStamps(audioSamples,  feature_series, frameSize, sampleRate):
    '''
    utility function to get timestamps
    '''
    import essentia
    duration = essentia.standard.Duration()
    duration_ = duration(audioSamples)
    
    frame_num = duration_ / float(len(feature_series))
    timestamps = np.arange(len(feature_series)) *  frame_num
    
    timestamps += (float(frameSize / 2) / sampleRate) # first frame centered at mid of window
    return timestamps


def stereo_to_MonoChunk(wavFileURI, begin_ts=0, end_ts=None, URIRecordingChunkResynthesized=None):
        '''
        convert a segment of stereo audio to mono
        uses essentia 
        '''
        import essentia
        sampleRate = 44100
        loader = essentia.standard.MonoLoader(filename=wavFileURI, sampleRate=sampleRate)
        audio = loader()
        if end_ts==None: # whole audio
            chunk_of_audio = audio
            output_wavFileURI = wavFileURI
        elif URIRecordingChunkResynthesized == None:
            sys.exit('please provide name for new chunk of audio')
        else:
            chunk_of_audio = audio[int(begin_ts * sampleRate):int(end_ts * sampleRate)]
            output_wavFileURI = URIRecordingChunkResynthesized
        monoWriter = essentia.standard.MonoWriter(filename=output_wavFileURI)
        monoWriter(chunk_of_audio)
        return output_wavFileURI

def load_audio_mono(filein, with_normalization_max=0):
    '''
    load audio as float array using scipy. If stereo, average channels to mono
    '''
    sampleRate, audioObj = scipy.io.wavfile.read(filein)  
    audioObj = audioObj.astype('float')
    
    if with_normalization_max:
        try:
            maxv = np.finfo(audioObj.dtype).max
        except:
            maxv = np.iinfo(audioObj.dtype).max
    
        audioObj /= maxv
      

    if (len(audioObj.shape))>1 and (audioObj.shape[1]>1): # stereo-to-mono. average the two channels
            audioObj[:,0] = (audioObj[:,0] + audioObj[:,1]) / 2
            audioObj = audioObj[:,0]  
    return audioObj, sampleRate
    

def delta(data, width=9, order=1, axis=-1, trim=True):
    r'''Compute delta features: local estimate of the derivative
    of the input data along the selected axis.
    
    Copied from librosa

    Parameters
    ----------
    data      : np.ndarray
        the input data matrix (eg, spectrogram)

    width     : int >= 3, odd [scalar]
        Number of frames over which to compute the delta feature

    order     : int > 0 [scalar]
        the order of the difference operator.
        1 for first derivative, 2 for second, etc.

    axis      : int [scalar]
        the axis along which to compute deltas.
        Default is -1 (columns).

    trim      : bool
        set to `True` to trim the output matrix to the original size.

    Returns
    -------
    delta_data   : np.ndarray [shape=(d, t) or (d, t + window)]
        delta matrix of `data`.

    Notes
    -----
    This function caches at level 40.

    '''

    data = np.atleast_1d(data)

    if width < 3 or np.mod(width, 2) != 1:
#         raise ParameterError('width must be an odd integer >= 3')
        sys.exit('width must be an odd integer >= 3')

    if order <= 0 or not isinstance(order, int):
        sys.exit('order must be a positive integer')

    half_length = 1 + int(width // 2)
    window = np.arange(half_length - 1., -half_length, -1.)

    # Normalize the window so we're scale-invariant
    window /= np.sum(np.abs(window)**2)

    # Pad out the data by repeating the border values (delta=0)
    padding = [(0, 0)] * data.ndim
    width = int(width)
    padding[axis] = (width, width)
    delta_x = np.pad(data, padding, mode='edge')

    for _ in range(order):
        delta_x = scipy.signal.lfilter(window, 1, delta_x, axis=axis)

    # Cut back to the original shape of the input data
    if trim:
        idx = [slice(None)] * delta_x.ndim
        idx[axis] = slice(- half_length - data.shape[axis], - half_length)
        delta_x = delta_x[idx]

    return delta_x


def preemph(x,alpha):
    y = np.array(x, copy=True)
    y[1:] -= alpha * y[:-1]
    y[0] *= (1.0 - alpha)
    return y

def next_power_of_two(x):
    '''
    return next power of 2 >= x
    uses shift bit length
    
    '''
    return 1<<(x-1).bit_length()

