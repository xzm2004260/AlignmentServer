import subprocess
import os
import glob
import sys

## variant 1. Deep Conv Sep source separation
PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset150/'

## variant 2. audionamix source sep.
PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset_29_voice_separation/Metal/'
PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset_29_voice_separation/R&B/'
PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset_29_voice_separation/Alternatives/'
# PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset_29_voice_separation/Blues/'
# PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset_29_voice_separation/HipHop/'

def doit(argv):
    
    if len(argv) != 2:
        sys.exit(f'Usage: {argv[0]} <0=deepconvsep, 1=Audionamix>')
    # small dataset
    separation_audionamix = int(argv[1])
    if separation_audionamix:
        PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/19-lyrics/audionamix_separated'
    else:
        PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/19-lyrics/'
    
     
    a = os.path.join(PATH_DATA, "*.wav");
    wav_files = glob.glob(a)
    
    b = os.path.join(PATH_DATA, "*.mp3");
    mp3_files  = glob.glob(b)
    
    ## ffmpeg
    if not wav_files:
        for mp3 in mp3_files:
        	basename = os.path.splitext(mp3)[0]
        	if not os.path.exists(f'{basename}.wav'):
        		pipe = subprocess.Popen(['ffmpeg','-i',f'{mp3}',f'{basename}.wav'])
        		pipe.wait()
    
    a = os.path.join(PATH_DATA, "*.wav")
    wav_files = glob.glob(a)
    
    for wav in wav_files:
         basename = os.path.splitext(wav)[0]
    
    # with _vocal_suffix
         if separation_audionamix: 
    # no vocal suffix
             a = ['python3', '/Users/joro/workspace/AlignmentServer/src/align/doit.py', f'{wav}',f'{basename[:-6]}.txt','2','0', f'{basename[:-6]}.lab'] # -6 : skip the automatically generated -vocal suffix
         else:
             a = ['python3', '/Users/joro/workspace/AlignmentServer/src/align/doit.py', f'{wav}',f'{basename}.txt','2', '1',f'{basename}.lab'] # 
    
         print(' '.join(a))
         print(basename)
         if basename in ['/Users/joro/Documents/VOICE_magix/Lyric_find/dataset150/Bjork - Undo', '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset150/Stacey Q - Two of Hearts']: 
         	continue # errors on these files
         if not os.path.exists(f'{basename}.lab'):
             subprocess.check_call(a)

if __name__ == '__main__':
    doit(sys.argv)