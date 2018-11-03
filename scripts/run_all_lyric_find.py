import subprocess
import os
import glob

PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset150/'
PATH_DATA = '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset_29_voice_separation/Metal/'

a = os.path.join(PATH_DATA, "*.wav");
wav_files = glob.glob(a)

b = os.path.join(PATH_DATA, "*.mp3");
mp3_files  = glob.glob(b)


# for mp3 in mp3_files:
# 	basename = os.path.splitext(mp3)[0]
# 	if not os.path.exists(f'{basename}.detected.txt'):
# 		pipe = subprocess.Popen(['ffmpeg','-i',f'{mp3}',f'{basename}.wav'])
# 		pipe.wait()

for wav in wav_files:
     basename = os.path.splitext(wav)[0]
     a = ['python3', 'src/align/doit.py', f'{wav}',f'{basename}.txt','2', f'{basename}.detected.txt']
     print(' '.join(a))
     print(basename)
     if basename in ['/Users/joro/Documents/VOICE_magix/Lyric_find/dataset150/Bjork - Undo', '/Users/joro/Documents/VOICE_magix/Lyric_find/dataset150/Stacey Q - Two of Hearts']: 
     	continue # errors on these files
     if not os.path.exists(f'{basename}.detected.txt'):
         subprocess.check_call(a)